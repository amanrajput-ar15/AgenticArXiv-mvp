"""MCPController for billing API with server error handling."""
import os
import time
from typing import Any

from google import genai
from langfuse import Langfuse
from dotenv import load_dotenv

from agenticarxiv.mcp.memory import Memory
from agenticarxiv.vectorstore.faiss_store import FAISSStore
from agenticarxiv.ingestion.embedder import Embedder

load_dotenv()

AGENT_ORDER = ["literature", "methods", "results", "critique", "synthesis"]


class MCPController:
    """Production controller for billing API with error resilience."""
    
    def __init__(
        self,
        vector_store: FAISSStore,
        embedder: Embedder,
        db=None,
        job_id: str | None = None,
        llm_model: str = "gemini-2.5-flash",
    ):
        self.vector_store = vector_store
        self.embedder = embedder
        self.db = db
        self.job_id = job_id
        self.llm_model = llm_model
        self.memory = Memory()
        self.agents: dict[str, Any] = {}
        
        # Shared client for connection reuse
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.langfuse = Langfuse()
        
        # Inter-agent delay for billing tier (prevents burst)
        self.inter_agent_delay = 0.5  # 500ms between agents

    def register_agent(self, name: str, agent: Any) -> None:
        """Register agent with shared client."""
        agent.client = self.client
        self.agents[name] = agent

    def retrieve_context(self, query: str, k: int = 15) -> list[dict]:
        """Retrieve from FAISS."""
        query_embedding = self.embedder.embed_text(query, task_type="RETRIEVAL_QUERY")
        return self.vector_store.search(query_embedding, k=k)

    def orchestrate(self, query: str, retrieval_k: int = 15) -> dict:
        """Execute all 5 agents with error resilience."""
        self.memory.add_query(query)
        
        trace = self.langfuse.trace(
            name="research-orchestration",
            input={"query": query, "retrieval_k": retrieval_k},
            metadata={"job_id": self.job_id, "tier": "billing"},
        )

        context = self.retrieve_context(query, k=retrieval_k)
        if not context:
            raise ValueError("Vector store empty. Upload papers first.")

        results: dict = {}
        failed_agents = []
        total_retries = 0

        for i, agent_name in enumerate(AGENT_ORDER):
            # Small delay between agents to prevent burst
            if i > 0:
                time.sleep(self.inter_agent_delay)
            
            span = trace.span(
                name=f"agent-{agent_name}",
                input={"context_chunks": len(context)},
            )
            
            try:
                result = self.agents[agent_name].execute(query, context, self.client)
                total_retries += result.get("retries", 0)
                
                if result.get("status") == "failed":
                    failed_agents.append(agent_name)
                
            except Exception as e:
                # Catch unexpected errors
                result = {
                    "agent": agent_name,
                    "analysis": f"[Unexpected error: {e}]",
                    "sources_used": 0,
                    "retries": 0,
                    "status": "failed"
                }
                failed_agents.append(agent_name)

            span.end(
                output={"analysis_length": len(result.get("analysis", ""))},
                metadata={
                    "sources_used": result.get("sources_used", 0),
                    "retries": result.get("retries", 0),
                    "status": result.get("status", "unknown")
                },
            )
            
            results[agent_name] = result
            self.memory.add_agent_result(agent_name, result)

            # Progressive write
            if self.db is not None and self.job_id is not None:
                self.db.jobs.update_one(
                    {"_id": self.job_id},
                    {
                        "$set": {
                            f"result.{agent_name}": result.get("analysis", ""),
                            "agents_completed": list(results.keys()),
                            "total_retries": total_retries,
                        }
                    },
                )

        # Compile report
        final_report = self._compile_report(query, results, context)
        final_report["total_retries"] = total_retries
        final_report["failed_agents"] = failed_agents
        final_report["success_rate"] = f"{5 - len(failed_agents)}/5"

        trace.update(
            output={
                "sections": list(results.keys()),
                "num_sources": final_report["num_sources"],
                "total_retries": total_retries,
                "failed_count": len(failed_agents),
            }
        )
        self.langfuse.flush()
        
        return final_report

    def _compile_report(self, query: str, agent_results: dict, context: list[dict]) -> dict:
        """Assemble final report."""
        sources = list({
            c.get("paper_id"): {
                "paper_id": c.get("paper_id"),
                "title": c.get("title"),
                "authors": c.get("authors"),
                "published": c.get("published"),
            }
            for c in context if c.get("paper_id")
        }.values())
        
        return {
            "query": query,
            "literature_review": agent_results.get("literature", {}).get("analysis", ""),
            "methods_analysis": agent_results.get("methods", {}).get("analysis", ""),
            "results_analysis": agent_results.get("results", {}).get("analysis", ""),
            "critique": agent_results.get("critique", {}).get("analysis", ""),
            "synthesis": agent_results.get("synthesis", {}).get("analysis", ""),
            "sources": sources,
            "num_sources": len(sources),
            "agents_run": list(agent_results.keys()),
        }