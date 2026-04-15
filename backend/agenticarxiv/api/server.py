"""FastAPI routing layer — validates, writes file, pushes to queue.
The server does exactly three things per upload:
  1. Validate request
  2. Write PDF to disk
  3. Push job_id to queue
It returns in <100ms. It NEVER processes the file inline.
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import redis
import uuid
import os
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AgenticArXiv", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", "https://your-app.vercel.app"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mongo = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db    = mongo["agenticarxiv"]
queue = redis.from_url(os.getenv("VALKEY_URL", "redis://localhost:6379"))

VOLUME     = Path(os.getenv("VOLUME_PATH", "./data"))
UPLOAD_DIR = VOLUME / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class ResearchRequest(BaseModel):
    query: str
    retrieval_k: int = 15


def _create_job(job_type: str, extra: dict) -> str:
    """Insert a job doc into MongoDB and push the ID onto the Valkey queue."""
    job_id = str(uuid.uuid4())
    db.jobs.insert_one({
        "_id":              job_id,
        "type":             job_type,
        "status":           "PENDING",
        "created_at":       datetime.now(timezone.utc),
        "result":           {},
        "error":            None,
        "agents_completed": [],
        **extra,
    })
    queue.lpush("agenticarxiv:jobs", job_id)
    return job_id


@app.get("/")
def root():
    return {"message": "AgenticArXiv API v3.0.0", "status": "running"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Accept a PDF, write it to the shared volume, enqueue an ingest job."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files accepted")

    contents = await file.read()
    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 50MB)")

    file_id   = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}.pdf"
    file_path.write_bytes(contents)  # server's ONLY interaction with file content

    job_id = _create_job("ingest", {
        "file_path":      str(file_path),
        "original_name":  file.filename,
    })
    return {"job_id": job_id, "status": "PENDING"}


@app.post("/research")
def research(req: ResearchRequest):
    """Enqueue a research job for the given query."""
    job_id = _create_job("research", {"input": req.model_dump()})
    return {"job_id": job_id, "status": "PENDING"}


@app.get("/status/{job_id}")
def status(job_id: str):
    """Poll job status. Frontend polls this every 2 seconds."""
    job = db.jobs.find_one({"_id": job_id}, {"_id": 0})
    if not job:
        raise HTTPException(404, "Job not found")
    # Convert datetime objects to ISO strings for JSON serialisation
    for key in ("created_at", "started_at", "completed_at"):
        if key in job and job[key] is not None:
            job[key] = job[key].isoformat()
    return job


@app.get("/health")
def health():
    """Returns vector store chunk count — used by the Navbar status pill."""
    try:
        from agenticarxiv.vectorstore.faiss_store import FAISSStore
        store = FAISSStore()
        return {"status": "ok", "total_chunks": store.index.ntotal}
    except Exception:
        return {"status": "ok", "total_chunks": 0}


@app.delete("/vectorstore")
def clear_vectorstore():
    """Dev utility — wipe and rebuild the FAISS index."""
    from agenticarxiv.vectorstore.faiss_store import FAISSStore
    store = FAISSStore()
    store.clear()
    return {"status": "vector store cleared"}


@app.get("/jobs")
def list_jobs(limit: int = 20):
    """Dev utility — list recent jobs."""
    jobs = list(db.jobs.find({}, {"_id": 1, "type": 1, "status": 1, "created_at": 1})
                .sort("created_at", -1).limit(limit))
    for j in jobs:
        j["job_id"] = j.pop("_id")
        if "created_at" in j and j["created_at"]:
            j["created_at"] = j["created_at"].isoformat()
    return {"jobs": jobs}