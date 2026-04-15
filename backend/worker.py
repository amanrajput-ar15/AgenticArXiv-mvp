"""AgenticArXiv Worker — BRPOP loop, all heavy processing lives here.

The API server NEVER opens files or calls Gemini.
The worker does ALL of:
  - PDF → PNG pages (pdf2image + poppler)
  - PNG → structured text (Gemini 2.5 Flash vision, cached)
  - Text → chunks (500-word sliding window, 50-word overlap)
  - Chunks → embeddings (Gemini text-embedding-004, 768-dim)
  - Embeddings → FAISS (fcntl write lock)
  - Research queries → 5 agents → Langfuse traces → progressive MongoDB writes

Run in a separate terminal from the API server:
  python worker.py
"""
import redis
import os
import traceback
from datetime import datetime, timezone
from pymongo import MongoClient
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from agenticarxiv.ingestion.vision_extractor import extract_pdf_text
from agenticarxiv.ingestion.pdf_to_images import pdf_to_images
from agenticarxiv.ingestion.chunker import Chunker
from agenticarxiv.ingestion.embedder import Embedder
from agenticarxiv.vectorstore.faiss_store import FAISSStore
from agenticarxiv.mcp.controller import MCPController
from agenticarxiv.agents.literature import LiteratureAgent
from agenticarxiv.agents.methods import MethodsAgent
from agenticarxiv.agents.results import ResultsAgent
from agenticarxiv.agents.critique import CritiqueAgent
from agenticarxiv.agents.synthesis import SynthesisAgent

mongo  = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db     = mongo["agenticarxiv"]
queue  = redis.from_url(os.getenv("VALKEY_URL", "redis://localhost:6379"))
VOLUME = Path(os.getenv("VOLUME_PATH", "./data"))


def build_controller(job_id: str) -> MCPController:
    """Construct a fully registered MCPController for a research job."""
    store    = FAISSStore()
    embedder = Embedder()
    ctrl     = MCPController(
        vector_store=store,
        embedder=embedder,
        db=db,
        job_id=job_id,
        llm_model="gemini-2.5-flash",
    )
    ctrl.register_agent("literature", LiteratureAgent())
    ctrl.register_agent("methods",    MethodsAgent())
    ctrl.register_agent("results",    ResultsAgent())
    ctrl.register_agent("critique",   CritiqueAgent())
    ctrl.register_agent("synthesis",  SynthesisAgent())
    return ctrl


def process_ingest(job_id: str, file_path: str) -> None:
    """Full ingestion pipeline for a single PDF.

    Steps:
      1. PDF → PNG pages at 150 DPI
      2. PNG pages → structured text via Gemini 2.5 Flash vision (cached)
      3. Text → 500-word chunks with 50-word overlap
      4. Chunks → 768-dim embeddings (text-embedding-004)
      5. Embeddings → FAISS index (fcntl write lock)
      6. MongoDB status update: DONE
    """
    pdf_path = Path(file_path)
    img_dir  = VOLUME / "images" / job_id
    img_dir.mkdir(parents=True, exist_ok=True)

    print(f"  [ingest] {job_id}: converting PDF to images...")
    image_paths = pdf_to_images(str(pdf_path), str(img_dir), dpi=150)
    print(f"  [ingest] {job_id}: {len(image_paths)} pages")

    print(f"  [ingest] {job_id}: extracting text via Gemini vision...")
    full_text = extract_pdf_text(image_paths)

    print(f"  [ingest] {job_id}: chunking text...")
    chunks = Chunker().chunk_text(full_text, file_id=job_id)
    print(f"  [ingest] {job_id}: {len(chunks)} chunks created")

    print(f"  [ingest] {job_id}: embedding chunks...")
    chunks = Embedder().embed_chunks(chunks)

    print(f"  [ingest] {job_id}: writing to FAISS...")
    FAISSStore().add_chunks(chunks)

    db.jobs.update_one(
        {"_id": job_id},
        {
            "$set": {
                "status":          "DONE",
                "chunks_created":  len(chunks),
                "pages_processed": len(image_paths),
                "completed_at":    datetime.now(timezone.utc),
            }
        },
    )
    print(f"  [ingest] {job_id}: DONE — {len(chunks)} chunks in FAISS")


def process_research(job_id: str, input_data: dict) -> None:
    """Run the 5-agent research pipeline for a query.

    The controller handles:
      - FAISS retrieval
      - Sequential agent execution
      - Langfuse tracing (1 trace, 5 spans)
      - Progressive MongoDB write-back after each agent
    """
    print(f"  [research] {job_id}: starting orchestration...")
    ctrl   = build_controller(job_id)
    report = ctrl.orchestrate(**input_data)

    db.jobs.update_one(
        {"_id": job_id},
        {
            "$set": {
                "status":       "DONE",
                "result":       report,
                "completed_at": datetime.now(timezone.utc),
            }
        },
    )
    print(f"  [research] {job_id}: DONE — {report['num_sources']} sources")


def main() -> None:
    """BRPOP loop — blocks until a job arrives, zero CPU while idle.

    Known limitation (BRPOP at-most-once delivery):
      Worker crash mid-job = job removed from queue, stuck PROCESSING in MongoDB.
      Fix in v2: LMOVE to a processing list + supervisor re-queues stale jobs.
    """
    print("[worker] started — listening on agenticarxiv:jobs")
    print(f"[worker] volume: {VOLUME}")
    print(f"[worker] mongo:  {os.getenv('MONGO_URI', 'mongodb://localhost:27017')}")
    print(f"[worker] valkey: {os.getenv('VALKEY_URL', 'redis://localhost:6379')}")

    while True:
        # BRPOP blocks until a job arrives — zero CPU while idle
        _, job_id_bytes = queue.brpop("agenticarxiv:jobs")
        job_id = job_id_bytes.decode()
        job    = db.jobs.find_one({"_id": job_id})

        if not job:
            print(f"[worker] WARNING: job {job_id} not found in MongoDB — skipping")
            continue

        print(f"[worker] picked up {job_id}  type={job['type']}")
        db.jobs.update_one(
            {"_id": job_id},
            {"$set": {"status": "PROCESSING", "started_at": datetime.now(timezone.utc)}},
        )

        try:
            if job["type"] == "ingest":
                process_ingest(job_id, job["file_path"])
            elif job["type"] == "research":
                process_research(job_id, job["input"])
            else:
                raise ValueError(f"Unknown job type: {job['type']}")
        except Exception as e:
            db.jobs.update_one(
                {"_id": job_id},
                {
                    "$set": {
                        "status":       "FAILED",
                        "error":        traceback.format_exc(),
                        "completed_at": datetime.now(timezone.utc),
                    }
                },
            )
            print(f"[worker] FAILED {job_id}: {e}")


if __name__ == "__main__":
    main()