"""BaseAgent with billing API error handling and retries."""
from __future__ import annotations
from abc import ABC, abstractmethod
import time
import random
import re
import os

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


class BaseAgent(ABC):
    """Production agent with resilience for billing API."""
    
    name: str = "base"
    temperature: float = 0.3
    max_retries: int = 3
    base_delay: float = 1.0  # 1 second base for billing tier
    
    def __init__(self):
        self.client = None
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        pass
    
    def _filter_context(self, context: list[dict]) -> list[dict]:
        return context
    
    def _format_context(self, context: list[dict]) -> str:
        seen, formatted = set(), []
        for chunk in context:
            header = ""
            if chunk.get("paper_id") not in seen:
                seen.add(chunk.get("paper_id"))
                authors = ", ".join((chunk.get("authors") or [])[:2])
                pub = (chunk.get("published") or "")[:10]
                title = chunk.get("title", "Untitled")
                header = f"\n[{title} — {authors} — {pub}]\n"
            formatted.append(header + chunk.get("text", ""))
        return "\n\n".join(formatted)
    
    def _is_retryable_error(self, error_str: str) -> bool:
        """Check if error is retryable (503, 429, etc.)."""
        retryable = ["503", "429", "RESOURCE_EXHAUSTED", "UNAVAILABLE", 
                     "QUOTA_EXHAUSTED", "RATE_LIMIT", "INTERNAL", "DEADLINE_EXCEEDED"]
        return any(code in error_str.upper() for code in retryable)
    
    def _extract_retry_delay(self, error_str: str) -> float | None:
        """Extract server-suggested retry delay."""
        # Try "retry in Xs" pattern
        match = re.search(r'retry in (\d+\.?\d*)s', error_str.lower())
        if match:
            return float(match.group(1))
        # Try "Retry-After: X" pattern
        match = re.search(r'retry-after[:\s]+(\d+)', error_str.lower())
        if match:
            return float(match.group(1))
        return None
    
    def execute(self, query: str, context: list[dict], shared_client=None) -> dict:
        """Execute with exponential backoff for server errors."""
        client = shared_client or self.client or genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )
        
        filtered_ctx = self._filter_context(context)
        ctx = self._format_context(filtered_ctx)
        prompt = f"Research Question: {query}\n\nRelevant Papers:\n{ctx}\n\nProvide your analysis:"
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=self._get_system_prompt(),
                        temperature=self.temperature,
                    ),
                )
                
                sources = len({c.get("paper_id") for c in filtered_ctx if c.get("paper_id")})
                return {
                    "agent": self.name,
                    "analysis": response.text,
                    "sources_used": sources,
                    "retries": attempt,
                    "status": "success"
                }
                
            except Exception as e:
                error_str = str(e)
                last_error = e
                
                # Check if retryable
                if not self._is_retryable_error(error_str):
                    # Non-retryable error (400, 401, 403, etc.)
                    return {
                        "agent": self.name,
                        "analysis": f"[Agent error: {e}]",
                        "sources_used": 0,
                        "retries": attempt,
                        "status": "failed"
                    }
                
                # Retryable error - calculate delay
                if attempt < self.max_retries - 1:
                    server_delay = self._extract_retry_delay(error_str)
                    
                    if server_delay:
                        # Use server suggestion + small jitter
                        wait_time = server_delay + random.uniform(0.5, 1.5)
                    else:
                        # Exponential backoff: 1s, 2s, 4s + jitter
                        wait_time = (self.base_delay * (2 ** attempt)) + random.uniform(0, 1)
                    
                    # Cap at 60 seconds
                    wait_time = min(wait_time, 60)
                    
                    print(f"  [agent-{self.name}] Server busy (503/429), retry {attempt + 1}/{self.max_retries} after {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    # Max retries exceeded
                    break
        
        # All retries failed
        return {
            "agent": self.name,
            "analysis": f"[Agent error after {self.max_retries} retries: {last_error}]",
            "sources_used": 0,
            "retries": self.max_retries,
            "status": "failed"
        }