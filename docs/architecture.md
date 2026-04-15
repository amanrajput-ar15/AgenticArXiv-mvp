# System Architecture: AgenticArXiv

## High-Level Design (HLD)

AgenticArXiv is a multi-agent autonomous research system that ingests arXiv papers via an async job queue, parses PDFs using Gemini 2.5 Flash vision, builds a FAISS 768-dim vector index, and orchestrates five specialized agents to produce structured research reports.

### Core Subsystems

1. **API Server (FastAPI)**
   - Thin routing layer: validates requests, writes files, enqueues jobs
   - Returns `job_id` in &lt;100ms, never processes inline
   - Endpoints: `/upload`, `/research`, `/status/{id}`, `/health`

2. **Async Job Queue (Redis/Valkey)**
   - BRPOP primitive for blocking, zero-CPU idle workers
   - Carries IDs only, not data (S3/SQS/Lambda pattern)

3. **Worker Process**
   - BRPOP loop: pulls job_id, executes heavy pipeline
   - PDF → images → Gemini vision → text → chunks → embeddings → FAISS
   - OR: Research → retrieval → 5 sequential agents → report

4. **Vector Store (FAISS)**
   - Local 768-dim IndexFlatL2 with dimension guard
   - File-lock protected writes, pickle metadata sync
   - No infra cost, forces understanding of internals

5. **Job State (MongoDB)**
   - Schema-free document store for job status, agent outputs, chunk metadata
   - Progressive write-back: frontend sees "3/5 agents done" in real-time

6. **Observability (Langfuse)**
   - Per-agent latency tracing, free 50k obs/month
   - One parent trace per research job, 5 child spans for agents