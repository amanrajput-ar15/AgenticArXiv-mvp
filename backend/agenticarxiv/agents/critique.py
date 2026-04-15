"""CritiqueAgent — limitations, weaknesses, open problems.

Context strategy: Keyword filter on limitation, weakness, challenge, future work.
Temperature: 0.3 (critical analysis should be grounded in paper text).
"""
from agenticarxiv.agents.base import BaseAgent

_SYSTEM_PROMPT = """You are a critical reviewer identifying weaknesses and open problems.
Analyze:
1. Explicitly stated limitations in each paper
2. Methodological weaknesses not acknowledged by the authors
3. Scalability and generalization concerns
4. Reproducibility issues (missing details, proprietary data, compute requirements)
5. Open problems and challenges the field has not yet solved
6. Potential negative societal impacts where relevant

FORMAT RULES:
- Use plain text only. NO markdown (no #, ##, **, *, - bullets).
- Use Title Case for section headers followed by a blank line.
- Use numbered lists (1., 2., 3.) for sequential items.
- Use line breaks to separate sections, not headers.

Be constructive, not dismissive. Distinguish between: (a) limitations the authors
acknowledge, (b) limitations you identify from the methodology, (c) open problems
in the field. Cite specific papers for each point."""

_KEYWORDS = {"limitation", "weakness", "challenge", "future work", "drawback",
             "constraint", "problem", "issue", "fail", "cannot", "unable",
             "difficult", "expensive", "scalab", "generaliz", "bias",
             "open question", "future research", "not addressed"}


class CritiqueAgent(BaseAgent):
    name        = "critique"
    temperature = 0.3

    @property
    def system_prompt(self) -> str:
        return _SYSTEM_PROMPT

    def _filter_context(self, context: list[dict]) -> list[dict]:
        """Keep chunks that discuss limitations and challenges."""
        filtered = [
            c for c in context
            if any(kw in c.get("text", "").lower() for kw in _KEYWORDS)
        ]
        return filtered if filtered else context