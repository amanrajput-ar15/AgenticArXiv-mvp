# Project Roadmap & Technical Debt

AgenticArXiv is currently backend-complete (v1.0). Frontend in progress.

## Immediate (v1.1)

- [ ] Web Worker for FAISS operations (offload from main thread)
- [ ] Streaming response for research queries (SSE instead of polling)
- [ ] Download report as Markdown

## Medium-Term (v1.5)

- [ ] arXiv search integration (direct paper download by ID)
- [ ] Multiple workers (Railway replicas for throughput)
- [ ] Parallel agent execution (paid Gemini tier)
- [ ] WebSocket real-time progress

## Long-Term (v2.0)

- [ ] Replace FAISS with Qdrant (native delete, metadata filtering)
- [ ] Chunk classification (methodology/results/limitation tags)
- [ ] Agent tool calling (web search, calculator)
- [ ] Self-improving agent loops