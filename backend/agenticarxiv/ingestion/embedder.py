"""Gemini text-embedding-004 embedder using google-genai SDK."""
import os
import time
import numpy as np
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


class Embedder:
    MODEL = "gemini-embedding-2-preview"
    DIM = 768

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def embed_text(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> np.ndarray:
        response = self.client.models.embed_content(
            model=self.MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=self.DIM,
            ),
        )
        return np.array(response.embeddings[0].values, dtype="float32")

    def embed_chunks(self, chunks: list[dict]) -> list[dict]:
        embedded = []
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = self.embed_text(
                chunk["text"], task_type="RETRIEVAL_DOCUMENT"
            )
            embedded.append(chunk)
            if (i + 1) % 50 == 0:
                time.sleep(1.0)
        return embedded