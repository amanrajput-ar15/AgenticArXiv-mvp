"""ResultsAgent — benchmark numbers and performance claims.

Context strategy: Keyword filter on result, benchmark, accuracy, dataset, SOTA.
Temperature: 0.3 (numbers must be precise).
"""
from agenticarxiv.agents.base import BaseAgent

_SYSTEM_PROMPT = """You are a results analyst focused on empirical performance in research papers.
Analyze:
1. Specific benchmark results with exact numbers (accuracy %, F1, BLEU, etc.)
2. Datasets used for evaluation and their characteristics
3. State-of-the-art comparisons — what the paper claims vs prior work
4. Statistical significance where reported
5. Reproducibility: are enough details given to replicate the results?

FORMAT RULES:
- Use plain text only. NO markdown.
- Write in flowing paragraphs, not lists.
- Connect ideas across papers naturally.

Always quote exact numbers. Never paraphrase quantitative claims.
Cite which paper reported each result."""

_KEYWORDS = {"result", "benchmark", "accuracy", "dataset", "performance",
             "score", "sota", "state-of-the-art", "baseline", "metric",
             "f1", "bleu", "rouge", "precision", "recall", "error rate",
             "evaluation", "experiment", "ablation", "table"}


class ResultsAgent(BaseAgent):
    name        = "results"
    temperature = 0.3

    @property
    def system_prompt(self) -> str:
        return _SYSTEM_PROMPT

    def _filter_context(self, context: list[dict]) -> list[dict]:
        """Keep chunks that discuss results and benchmarks."""
        filtered = [
            c for c in context
            if any(kw in c.get("text", "").lower() for kw in _KEYWORDS)
        ]
        return filtered if filtered else context