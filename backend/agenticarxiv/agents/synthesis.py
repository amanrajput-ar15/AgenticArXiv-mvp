"""SynthesisAgent — research gaps, cross-paper connections, future directions.

Context strategy: No filter — all top-10 chunks, broadest view.
Temperature: 0.4 (slightly higher — synthesis requires creative connection-making).

This is consistently the slowest agent (~8-10s) because it processes the
broadest context and generates the longest output. Confirmed in Langfuse traces.
"""
from agenticarxiv.agents.base import BaseAgent

_SYSTEM_PROMPT = """You are a research synthesizer identifying connections, gaps, and future directions.


Synthesize across ALL provided papers to:
1. Identify research gaps — what important questions remain unanswered?
2. Find cross-paper connections — where do findings reinforce or contradict each other?
3. Trace the trajectory of the field — where is it heading?
4. Propose concrete future research directions based on the gaps identified
5. Identify the most impactful contribution across the paper set

FORMAT RULES:
- Use plain text only. NO markdown.
- Write in flowing paragraphs, not lists.
- Connect ideas across papers naturally.

Do not summarize individual papers — synthesize ACROSS them.
Be specific about which papers you are connecting.
This section should provide insight a reader of the papers individually would miss."""


class SynthesisAgent(BaseAgent):
    name        = "synthesis"
    temperature = 0.4  # slightly higher for creative synthesis

    @property
    def system_prompt(self) -> str:
        return _SYSTEM_PROMPT

    def _filter_context(self, context: list[dict]) -> list[dict]:
        """No filter — synthesis needs the broadest view. Use top-10 chunks."""
        return context[:10]