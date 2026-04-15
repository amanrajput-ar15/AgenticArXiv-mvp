# AgenticArXiv — Performance Benchmarks

**Machine:** Windows 11, Intel i5, 16GB RAM  
**Date:** April 2026  
**Model:** gemini-2.5-flash (Google AI)  
**Embedding:** text-embedding-004 (768-dim)

---

## API Response Times

| Metric | Value |
|--------|-------|
| Upload request → job_id | ~50ms |
| Research request → job_id | ~30ms |
| Status poll (PENDING → DONE) | 2s intervals |

## Ingestion Pipeline

| Stage | Time |
|-------|------|
| PDF → PNG (10 pages, 150 DPI) | ~3s |
| PNG → Gemini vision extraction | ~15s (first run, no cache) |
| PNG → Cache hit | ~0.1s (subsequent runs) |
| Text → 500-word chunks | ~0.5s |
| Chunks → 768-dim embeddings | ~10s (10 chunks) |
| FAISS index write (file-locked) | ~0.2s |

**Total 10-page paper (cold):** ~30s  
**Total 10-page paper (cached):** ~5s

## Research Query

| Stage | Time |
|-------|------|
| Query embedding | ~0.5s |
| FAISS retrieval (k=15) | ~0.01s |
| Literature agent | ~3s |
| Methods agent | ~3s |
| Results agent | ~3s |
| Critique agent | ~3s |
| Synthesis agent | ~8s (slowest, broadest context) |

**Total 5-agent research:** ~20-25s

## Resource Usage

| Component | Usage |
|-----------|-------|
| FAISS index (3 chunks) | ~6KB |
| MongoDB storage | ~50KB per job |
| Redis memory | ~1KB per queued job |