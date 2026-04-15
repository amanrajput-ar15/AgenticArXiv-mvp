
---

## STEP 6: Create Root README.md

```markdown
# AgenticArXiv

[![Python](https://img.shields.io/badge/Python-3.13-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)]()
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-orange)]()

Multi-agent autonomous research system. Ingests arXiv papers via async queue, extracts text with Gemini vision, builds FAISS vector index, and orchestrates 5 specialized agents for structured research reports.

## Live Demo

[Coming soon — Day 13-14 deployment]

## Architecture


























## Quick Start

See [docs/README.md](./docs/README.md)

## Project Status

| Phase | Status |
|-------|--------|
| Backend (Days 1-7) | ✅ Complete |
| Frontend (Days 8-12) | ⏳ In Progress |
| Deployment (Days 13-15) | ⏳ Not Started |
| Polish + README (Days 16-18) | ⏳ Not Started |
| Twitter + Apply (Days 19-21) | ⏳ Not Started |

## Documentation

- [Architecture](./docs/architecture.md)
- [Benchmarks](./docs/benchmarks.md)
- [Decisions](./docs/decisions.md)
- [Roadmap](./docs/roadmap.md)

## Tech Stack

- **Backend:** FastAPI, MongoDB, Redis, FAISS, Gemini 2.5 Flash
- **Frontend:** Next.js 16, Tailwind CSS, Claude Design System
- **Deploy:** Railway (backend), Vercel (frontend)

## License

MIT