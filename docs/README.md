# AgenticArXiv

Multi-agent autonomous research system. Five specialized Gemini 2.5 Flash agents analyze arXiv papers and produce structured reports.

## Quick Start

### Prerequisites

- Python 3.13+
- Docker Desktop
- Gemini API key (free tier: 15 req/min, 1M tokens/day)

### 1. Clone & Setup

```bash
git clone &lt;your-repo&gt;
cd AgenticArXiv/backend
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt