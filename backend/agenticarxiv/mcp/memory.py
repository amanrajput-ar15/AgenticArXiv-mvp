"""Per-job in-memory state store.

Holds the conversation history, query, and agent results for a single
research job. Scoped to one MCPController instance (one job).
Not shared across workers — each worker has its own Memory object.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Memory:
    """Lightweight in-memory store for a single research job."""

    messages:      list[dict]       = field(default_factory=list)
    agent_results: dict[str, dict]  = field(default_factory=dict)
    queries:       list[str]        = field(default_factory=list)
    created_at:    str              = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def add_message(self, role: str, content: str) -> None:
        """Append a message to the conversation history."""
        self.messages.append({
            "role":       role,
            "content":    content,
            "timestamp":  datetime.now(timezone.utc).isoformat(),
        })

    def add_query(self, query: str) -> None:
        """Record the research query."""
        self.queries.append(query)

    def add_agent_result(self, agent_name: str, result: dict) -> None:
        """Store an agent's output."""
        self.agent_results[agent_name] = result

    def get_history(self) -> list[dict]:
        """Return the full message history."""
        return self.messages.copy()

    def get_agent_result(self, agent_name: str) -> dict | None:
        """Return a specific agent's result, or None if not yet run."""
        return self.agent_results.get(agent_name)

    def summary(self) -> dict:
        """Return a lightweight summary for logging."""
        return {
            "queries":         self.queries,
            "agents_run":      list(self.agent_results.keys()),
            "message_count":   len(self.messages),
            "created_at":      self.created_at,
        }