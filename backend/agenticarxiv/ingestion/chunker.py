"""500-word sliding window chunker with 50-word overlap.

Why sliding window?
- Preserves sentence context across chunk boundaries
- 50-word overlap ensures a sentence split at a boundary appears in both chunks
- 500-word size balances retrieval granularity vs embedding cost
"""
from __future__ import annotations


class Chunker:
    """Splits text into overlapping word-window chunks with metadata."""

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap    = overlap

    def chunk_text(
        self,
        text: str,
        file_id: str,
        title: str = "",
        authors: list[str] | None = None,
        published: str = "",
    ) -> list[dict]:
        """Split text into overlapping chunks with metadata.

        Args:
            text:      Full extracted text of the paper.
            file_id:   UUID of the uploaded file — becomes paper_id in FAISS metadata.
            title:     Paper title (optional — populated by arxiv_loader).
            authors:   List of author names (optional).
            published: ISO date string (optional).

        Returns:
            List of chunk dicts ready for Embedder.embed_chunks().
        """
        words  = text.split()
        chunks = []
        i      = 0
        idx    = 0

        while i < len(words):
            window = words[i : i + self.chunk_size]
            chunk_text = " ".join(window)

            chunks.append({
                "text":       chunk_text,
                "paper_id":   file_id,
                "chunk_index": idx,
                "title":      title,
                "authors":    authors or [],
                "published":  published,
                "word_count": len(window),
            })

            # Advance by (chunk_size - overlap) to create the sliding window
            i   += self.chunk_size - self.overlap
            idx += 1

        return chunks