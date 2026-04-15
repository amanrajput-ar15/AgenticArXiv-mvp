# AgenticArXiv

**Multi-Agent Autonomous Research System**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-4285F4?logo=google)](https://ai.google.dev)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?logo=next.js)](https://nextjs.org)
[![FAISS](https://img.shields.io/badge/FAISS-1.9-0077B6)](https://github.com/facebookresearch/faiss)
[![Langfuse](https://img.shields.io/badge/Langfuse-2.57-000000)](https://langfuse.com)

> Autonomous research system that ingests arXiv papers via async job queue, parses PDFs using Gemini 2.5 Flash vision, builds a FAISS 768-dim vector index, and orchestrates five specialized agents to produce structured research reports — with full Langfuse observability.

**Live Demo:** [https://your-app.vercel.app](https://your-app.vercel.app)  

---

## Table of Contents

- [What This Proves to Interviewers](#-what-this-proves-to-interviewers)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Performance Benchmarks](#-performance-benchmarks)
- [Tech Stack](#-tech-stack)
- [Key Implementation Details](#-key-implementation-details)
- [Failure Log & Recoveries](#-failure-log--recoveries)
- [What I Learned](#-what-i-learned)
- [API Reference](#-api-reference)
- [Next Steps](#-next-steps)
- [License](#-license)

---

##  What This Proves to Interviewers

| Skill | Evidence in This Project |
|-------|--------------------------|
| **System Design** | Async queue-based pipeline (S3/SQS/Lambda pattern) |
| **Production Debugging** | 7 distinct failure modes identified and resolved |
| **API Migration** | Handled breaking SDK changes (`google-generativeai` → `google-genai`) |
| **Observability** | Distributed tracing with Langfuse (per-agent latency) |
| **Resilience** | Circuit breakers, exponential backoff, graceful degradation |
| **Cost Optimization** | Single SDK discipline, adaptive agent selection |

---

##  Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT — Next.js 16                           │
│              Claude Design System: Parchment · Georgia · Terracotta     │
│                    /ingest · /research · StatusBadge (poll)             │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────────┐
│                    FASTAPI — API Server (Railway)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────────┐  │
│  │  POST       │  │  POST       │  │  GET /health                    │  │
│  │  /upload    │  │  /research  │  │  (FAISS stats)                  │  │
│  │  <100ms     │  │  <100ms     │  │                                 │  │
│  └──────┬──────┘  └──────┬──────┘  └─────────────────────────────────┘  │
│         │                │                                               │
│         └────────────────┴────────────┬──────────────────────────┐       │
│                                       ▼                          ▼       │
│  ┌──────────────────────────────────────────┐  ┌────────────────────┐    │
│  │         MongoDB (Job State)              │  │  Valkey (Queue)    │    │
│  │  {status, result, agents_completed,      │  │  [job_id, job_id]  │    │
│  │   error, timestamps, metadata}           │  │  BRPOP blocking    │    │
│  └──────────────────────────────────────────┘  └──────────┬─────────┘   │
│                                                           │              │
│  ┌────────────────────────────────────────────────────────▼───────────┐  │
│  │              Shared Persistent Volume (Railway)                    │  │
│  │  /uploads/*.pdf  /images/page_*.png  /embeddings/faiss.*          │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────── ┘
                          │
                          │ BRPOP (zero CPU when idle)
┌─────────────────────────▼──────────────────────────────────────────────┐
│                         WORKER — Background Processor                   │
│                                                                         │
│  INGEST PIPELINE:                                                       │
│    PDF → pdf2image (150 DPI) → PNG pages → Gemini 2.5 Flash Vision     │
│    → Structured text → 500-word chunks (50-word overlap)                │
│    → gemini-embedding-001 (768-dim) → FAISS + file lock                │
│                                                                         │
│  RESEARCH PIPELINE:                                                     │
│    FAISS search (k=15) → 5 agents sequential:                          │
│      1. Literature   (field evolution, key authors)                     │
│      2. Methods      (algorithms, architectures)                        │
│      3. Results      (benchmarks, performance)                          │
│      4. Critique     (limitations, open problems)                       │
│      5. Synthesis    (gaps, future directions)                          │
│    → Langfuse trace (1 trace, 5 spans)                                  │
│    → Progressive MongoDB writes (real-time frontend updates)            │
│                                                                         │
│  ALL LLM CALLS:   gemini-2.5-flash via google-genai SDK v1.71.0        │
│  ALL EMBEDDINGS:  gemini-embedding-001 (768-dim, forced output)         │
│  ZERO OpenAI dependency                                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Architecture Decision Log

| Decision | Alternative | Why I Chose This |
|----------|-------------|------------------|
| **Async queue (Redis)** | Sync processing | Railway 60s timeout; PDF takes 30–90s |
| **Gemini-only** | OpenAI + Gemini | Single SDK, single billing, vision built-in |
| **Vision PDF parsing** | pypdf text extraction | Preserves multi-column, equations, tables |
| **FAISS local** | Pinecone / Qdrant | No infra cost, forces understanding internals |
| **Sequential agents** | Parallel asyncio | Easier debugging, rate limit management |
| **Progressive writes** | Final result only | Frontend sees "3/5 agents complete" live |

---

##  Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for local MongoDB & Redis)
- A Google AI Studio API key with billing enabled

### Local Development

```bash
# 1. Clone
git clone https://github.com/yourusername/agenticarxiv.git
cd agenticarxiv/backend

# 2. Virtual environment
python -m venv venv
source venv/bin/activate       # Windows: .\\venv\\Scripts\\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start infrastructure via Docker
docker run -d --name mongo -p 27017:27017 mongo:7
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 5. Configure environment
cp .env.example .env
# Edit .env — set your GEMINI_API_KEY

# 6. Run API server and worker in separate terminals
python main.py      # Terminal 1: FastAPI server  → http://localhost:8000
python worker.py    # Terminal 2: Background worker

# 7. Smoke test
curl http://localhost:8000/health
curl -F "file=@test.pdf" http://localhost:8000/upload
```

### Deployment (Railway + Vercel)

```bash
# Push to GitHub
git add .
git commit -m "Production ready"
git push origin main
```

**Railway (backend + worker):**
1. New Project → Deploy from GitHub
2. Add **MongoDB** plugin
3. Add **Redis** plugin
4. Add **Volume** mounted at `/mnt/volume`
5. Set environment variables (`GEMINI_API_KEY`, `MONGO_URL`, `REDIS_URL`, `VOLUME_PATH`)
6. Deploy — Railway auto-detects `Procfile` / `railway.toml`

**Vercel (frontend):**
1. Import the `frontend/` directory
2. Set `NEXT_PUBLIC_API_URL` to your Railway service URL
3. Deploy

---

##  Performance Benchmarks

| Operation | Billing Tier | Free Tier | Estimated Cost |
|-----------|-------------|-----------|----------------|
| 1-page PDF ingest | ~30s | ~90s (with retries) | ~$0.001 |
| 5-agent research query | ~35s | ~120s (partial) | ~$0.002 |
| 10-page paper full pipeline | ~90s | Often fails | ~$0.003 |

**Estimated monthly cost at heavy usage:** < $2 USD

> Free-tier degradation is expected and handled gracefully via adaptive agent selection and exponential backoff. The system never crashes — it degrades and retries.

---

## 🛠️ Tech Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **LLM + Vision + Embeddings** | `google-genai` | 1.71.0 | Single SDK for all AI calls |
| **Primary Model** | `gemini-2.5-flash` | Latest | Fast, multimodal, vision-capable |
| **Embeddings** | `gemini-embedding-001` | 768-dim | Replaced deprecated `text-embedding-004` |
| **PDF → Images** | `pdf2image` + `poppler` | 1.17.0 | Render pages as PNG for vision input |
| **Vector Store** | `faiss-cpu` | 1.9.0 | Local, zero cost, dimension-guarded |
| **Job Queue** | Valkey (Redis-compatible) | 7.x | BRPOP blocking primitive |
| **Job State** | MongoDB | 7.x | Schema-free, progressive writes |
| **Backend** | FastAPI + Uvicorn | 0.115.6 | Async, auto-docs, production Python |
| **Frontend** | Next.js 16 | App Router | RSC + client boundary pattern |
| **Styling** | Tailwind CSS | 4.x | Design system tokens |
| **Observability** | Langfuse | 2.57.0 | Per-agent latency, full trace tree |
| **Deploy** | Railway + Vercel | — | Persistent volume + edge CDN |

---

##  Key Implementation Details

### 1. Cross-Platform File Locking

FAISS index writes are protected against concurrent corruption on both Unix and Windows:

```python
# faiss_store.py
try:
    import fcntl  # Unix / Linux / macOS
    def lock(f): fcntl.flock(f, fcntl.LOCK_EX)
except ImportError:
    import portalocker  # Windows fallback
    def lock(f): portalocker.lock(f, portalocker.LOCK_EX)
```

### 2. Dimension Guard (Silent Failure Prevention)

Embedding model migrations silently corrupt indexes without this check:

```python
def add_chunks(self, chunks):
    embeddings = np.array([c["embedding"] for c in chunks])

    # CRITICAL: Loud error on dimension mismatch
    if embeddings.shape[1] != self.DIMENSION:
        raise ValueError(
            f"Dimension mismatch: got {embeddings.shape[1]}, "
            f"expected {self.DIMENSION}. "
            "Switched embedding models? Delete index and rebuild."
        )
    self.index.add(embeddings)
```

### 3. Exponential Backoff with Jitter

Handles Gemini `429 RESOURCE_EXHAUSTED` and `503 UNAVAILABLE` gracefully:

```python
def execute_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
        except Exception as e:
            if "429" in str(e) or "503" in str(e):
                wait = (2 ** attempt) + random.uniform(0, 1)  # 1s, 2s, 4s + jitter
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Max retries exceeded")
```

### 4. Adaptive Agent Selection (Free Tier Optimization)

Runs only the agents needed based on query content and remaining API quota:

```python
def select_agents(query: str, quota_remaining: int) -> list[str]:
    selected = ["literature", "synthesis"]  # Always run — highest signal

    if quota_remaining >= 4 and "method" in query.lower():
        selected.append("methods")
    if quota_remaining >= 5 and "result" in query.lower():
        selected.append("results")
    # critique added only with full quota
    if quota_remaining >= 6:
        selected.append("critique")

    return selected
```

### 5. Progressive MongoDB Writes

Each agent writes its result immediately — the frontend can display partial reports in real time:

```python
# After each agent completes:
db.jobs.update_one(
    {"_id": job_id},
    {
        "$set": {
            f"result.{agent_name}": agent_output,
            "agents_completed": completed_count,
            "status": "IN_PROGRESS"
        }
    }
)
```

### 6. Ingest Pipeline (Vision-Based PDF Parsing)

```python
# worker.py — ingest path
pages = convert_from_path(pdf_path, dpi=150)           # pdf2image
for i, page in enumerate(pages):
    page.save(f"/images/page_{i}.png", "PNG")

    with open(f"/images/page_{i}.png", "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {"mime_type": "image/png", "data": image_data},
            "Extract all text from this page. Preserve structure."
        ]
    )
    text = response.text

# Chunk → embed → add to FAISS
chunks = chunk_text(text, size=500, overlap=50)
for chunk in chunks:
    embedding = embed(chunk)
    faiss_store.add({"text": chunk, "embedding": embedding})
```

---

##  Failure Log & Recoveries

Every bug here was hit in production. Documenting them is the point.

| # | Failure | Root Cause | Fix Applied |
|---|---------|------------|-------------|
| 1 | `ModuleNotFoundError: fcntl` | Developed on Windows, deployed to Linux | Added cross-platform `portalocker` abstraction |
| 2 | `404 NOT_FOUND` on embedding model | SDK migration broke model name (`google-generativeai` → `google-genai`) | Switched to `gemini-embedding-001` |
| 3 | `403 PERMISSION_DENIED` on API calls | API key flagged due to billing issue | Generated new key on billing-enabled project |
| 4 | `AttributeError: Langfuse has no attribute trace()` | Langfuse v4.x breaking change | Pinned to `langfuse==2.57.0` |
| 5 | `Database objects do not implement bool()` | PyMongo cursor used in boolean context | Replaced with explicit `is not None` checks |
| 6 | `Cannot create field 'literature' in element {result: null}` | MongoDB update on null field | Initialize job document with `result: {}` at creation |
| 7 | `503 UNAVAILABLE` / `429 RESOURCE_EXHAUSTED` | Gemini rate limits on free tier | Exponential backoff with jitter; adaptive agent selection |

---

##  What I Learned

### System Design Patterns

- **Async job queues decouple acceptance from processing** — the API returns in <100ms regardless of how long the PDF takes to process
- **Queue carries IDs, not data** — this is the S3/SQS/Lambda pattern: storage holds bytes, queue carries the key, worker reads from storage
- **Progressive writes over final-only results** — users see real-time progress; resilience improves because partial results survive worker crashes

### Production Resilience

- Retry with exponential backoff + jitter prevents thundering herd on rate limit recovery
- Dimension guards catch silent data corruption that would otherwise surface as mysteriously bad search results
- Graceful degradation (adaptive agents) means the system is useful even when quotas are low

### Cost Engineering

- Single SDK (`google-genai`) reduces complexity, billing fragmentation, and debugging surface area
- Vision-based PDF parsing eliminates an entire OCR dependency layer
- Local FAISS vs. managed vector DB: forces you to understand ANN internals, and the cost delta at this scale is ~$20/month

### API Migration in Production

- Breaking SDK changes (`google-generativeai` → `google-genai`) require auditing every model string, embedding call, and content format
- Always pin dependencies in `requirements.txt` — never use `>=` in production

---

##  API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload a PDF file; enqueues an ingest job |
| `POST` | `/research` | Submit a research query; enqueues an analysis job |
| `GET` | `/status/{job_id}` | Poll job status and retrieve partial/full results |
| `GET` | `/health` | System health check with FAISS stats |
| `DELETE` | `/vectorstore` | Clear the FAISS index (development utility) |

### Request / Response Examples

#### Upload a PDF

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@paper.pdf"
```

```json
{ "job_id": "abc123", "status": "PENDING" }
```

#### Poll Ingest Status

```bash
curl http://localhost:8000/status/abc123
```

```json
{
  "status": "DONE",
  "chunks_created": 15,
  "pages_processed": 3,
  "duration_seconds": 28.4
}
```

#### Submit Research Query

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "attention mechanisms in transformers", "retrieval_k": 15}'
```

```json
{ "job_id": "def456", "status": "PENDING" }
```

#### Get Full Research Report

```bash
curl http://localhost:8000/status/def456
```

```json
{
  "status": "DONE",
  "agents_completed": 5,
  "result": {
    "literature": "The transformer architecture was introduced...",
    "methods": "The multi-head attention mechanism computes...",
    "results": "On WMT 2014 English-to-German translation...",
    "critique": "The O(n²) attention complexity limits...",
    "synthesis": "Future directions include linear attention variants..."
  }
}
```

#### Health Check

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "healthy",
  "faiss": {
    "total_vectors": 247,
    "dimension": 768,
    "index_type": "IndexFlatL2"
  },
  "queue_length": 0
}
```

---

##  Project Structure

```
agenticarxiv/
├── backend/
│   ├── main.py              # FastAPI app, route definitions
│   ├── worker.py            # Background processor (ingest + research pipelines)
│   ├── faiss_store.py       # FAISS wrapper with dimension guard + file locking
│   ├── agents.py            # Five research agents + adaptive selection
│   ├── chunker.py           # 500-word chunking with 50-word overlap
│   ├── requirements.txt     # Pinned dependencies
│   └── .env.example         # Environment variable template
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Landing / ingest UI
│   │   ├── research/
│   │   │   └── page.tsx     # Query UI + results display
│   │   └── layout.tsx       # Design system tokens
│   ├── components/
│   │   └── StatusBadge.tsx  # Polling component (PENDING → IN_PROGRESS → DONE)
│   └── package.json
└── README.md
```

---

##  Next Steps

- [ ] WebSocket / SSE for true real-time progress (replace polling)
- [ ] Parallel agent execution with `asyncio.gather` (paid tier only)
- [ ] Qdrant migration (native delete, metadata filtering, namespaces)
- [ ] Chunk classification at ingestion (tag chunks as methods / results / limitations)
- [ ] arXiv API integration (direct paper search & download by arXiv ID)
- [ ] Multi-paper synthesis (cross-document retrieval and comparison)
- [ ] Frontend agent trace viewer (Langfuse timeline embedded in UI)

---

##  License

MIT — Built for learning and portfolio demonstration.
