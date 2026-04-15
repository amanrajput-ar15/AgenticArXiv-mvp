# Architecture Decision Log
# AgenticArXiv

---

## Why async queue over synchronous processing

Synchronous: POST /upload → 60s processing → response. Fails at 60s timeout on Railway.

Async: POST /upload → 50ms response with job_id. Worker processes in background. User polls for status. Scales to 20-page papers without timeout.

---

## Why Gemini 2.5 Flash vision over pypdf

pypdf destroys multi-column layouts, corrupts equations, fails on scanned papers.

Gemini 2.5 Flash reads visual layout natively — columns as columns, tables as tables, equations preserved. Same SDK for LLM, vision, embeddings. One API key.

Tradeoff: ~15s per page first run. Mitigated by disk cache (file hash) — never re-extract same paper.

---

## Why sequential agents over parallel

Gemini free tier: 15 req/min limit. 5 parallel agents = rate limit hit immediately.

Sequential: simpler to debug, predictable latency, works on free tier. Parallel in v2 roadmap for paid tier.

---

## Why FAISS with dimension guard over Pinecone/Chroma

FAISS: zero infra cost, forces understanding of vector indexing internals.

Dimension guard: silent wrong retrieval is worse than loud error. Raises immediately if embedding model changes (1536→768).

---

## Why file-lock over database for FAISS writes

FAISS is in-memory + file-backed. Concurrent writes corrupt index. fcntl.LOCK_EX ensures single writer. Reads are concurrent, no lock needed.

---

## Why progressive write-back over final write only

5 extra MongoDB writes. User sees agents complete one-by-one in real-time vs 50s blank screen. Better UX for multi-step jobs.

---

## Why google-genai SDK over google-generativeai

google-generativeai deprecated April 2026. FutureWarning on import. google-genai is official replacement, cleaner API (Client instantiation vs global config).

---

## Why Docker local over MongoDB Atlas + Upstash for dev

Local: zero latency, zero cost, works offline. Same Redis/MongoDB interface. Cloud for production only.