"""MethodsAgent — architecture comparisons and design decisions.

Context strategy: Keyword filter on method, algorithm, architecture, training, loss.
Temperature: 0.3 (technical precision required).
"""
from agenticarxiv.agents.base import BaseAgent

_SYSTEM_PROMPT = """You are a technical methods analyst specializing in research methodology.
Analyze:
1. Specific algorithms, architectures, and technical approaches used
2. Training procedures, loss functions, and optimization strategies
3. Comparative analysis of methodological choices across papers
4. Implementation details that matter for reproducibility
5. Why each design decision was made (based on what the authors state)

FORMAT RULES:
- Use plain text only. NO markdown.
- Present numbers directly: "Accuracy: 94.5%" not "**Accuracy:** 94.5%"
- Use line breaks between different results.
- Cite paper names in quotes when referencing specific results.

Be precise with technical terminology. Cite the specific paper for each claim."""

_KEYWORDS = {"method", "algorithm", "architecture", "training", "loss",
             "model", "layer", "network", "parameter", "gradient",
             "optimization", "encoder", "decoder", "attention"}


class MethodsAgent(BaseAgent):
    name        = "methods"
    temperature = 0.3

    @property
    def system_prompt(self) -> str:
        return _SYSTEM_PROMPT

    def _filter_context(self, context: list[dict]) -> list[dict]:
        """Keep chunks that mention methods-related keywords."""
        filtered = [
            c for c in context
            if any(kw in c.get("text", "").lower() for kw in _KEYWORDS)
        ]
        # Fall back to full context if filter is too aggressive
        return filtered if filtered else context