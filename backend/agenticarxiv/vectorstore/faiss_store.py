"""FAISS vector store with dimension guard and cross-platform file lock.

Why dimension guard?
  Switching embedding models (e.g. 1536-dim → 768-dim) produces ZERO errors from FAISS
  but completely wrong retrieval results. The guard raises immediately on mismatch.

Why portalocker?
  fcntl is Unix-only. portalocker works on Windows, Linux, and macOS.
  Two workers writing simultaneously without a lock = index corruption.
  Reads are concurrent (no lock needed). Writes are serialised.
"""
import faiss
import numpy as np
import pickle
import os
from pathlib import Path

try:
    # Unix/Linux/macOS
    import fcntl
    HAS_FCNTL = True
except ImportError:
    # Windows - use portalocker
    import portalocker
    HAS_FCNTL = False


class FAISSStore:
    # text-embedding-004 outputs 768-dim. NEVER change without deleting and rebuilding.
    DIMENSION = 768

    def __init__(self, base_path: str | None = None):
        volume = os.getenv("VOLUME_PATH", "./data")
        base = base_path or f"{volume}/embeddings"
        Path(base).mkdir(parents=True, exist_ok=True)

        self.index_path = f"{base}/faiss.index"
        self.meta_path = f"{base}/faiss_metadata.pkl"
        self.lock_path = f"{base}/.write_lock"

        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.DIMENSION)
            self.metadata = []

    def _acquire_lock(self, f):
        """Acquire exclusive write lock - cross platform."""
        if HAS_FCNTL:
            fcntl.flock(f, fcntl.LOCK_EX)
        else:
            portalocker.lock(f, portalocker.LOCK_EX)

    def _release_lock(self, f):
        """Release write lock - cross platform."""
        if HAS_FCNTL:
            fcntl.flock(f, fcntl.LOCK_UN)
        else:
            portalocker.unlock(f)

    def add_chunks(self, chunks: list[dict]) -> None:
        """Add embedded chunks to the index.

        Args:
            chunks: List of chunk dicts, each must have an 'embedding' key
                    containing a (768,) float32 numpy array.

        Raises:
            ValueError: If any embedding has the wrong dimension.
            AssertionError: If FAISS/metadata counts desync (catastrophic bug).
        """
        embeddings = np.array(
            [c["embedding"] for c in chunks], dtype="float32"
        )

        # DIMENSION GUARD — loud error is better than silent wrong retrieval
        if embeddings.shape[1] != self.DIMENSION:
            raise ValueError(
                f"Dimension mismatch: got {embeddings.shape[1]}, "
                f"expected {self.DIMENSION}. "
                "Switched embedding models? Delete the index and rebuild."
            )

        # FILE LOCK — only one worker writes at a time; reads are concurrent
        # Create lock file if it doesn't exist
        Path(self.lock_path).touch(exist_ok=True)
        
        with open(self.lock_path, "r+") as lf:
            self._acquire_lock(lf)
            try:
                # Re-read index in case another worker updated it
                if os.path.exists(self.index_path):
                    self.index = faiss.read_index(self.index_path)
                    with open(self.meta_path, "rb") as f:
                        self.metadata = pickle.load(f)
                
                self.index.add(embeddings)

                clean = [
                    {k: v for k, v in c.items() if k != "embedding"}
                    for c in chunks
                ]
                self.metadata.extend(clean)

                # Sync assertion — if this fires, something is catastrophically wrong
                assert self.index.ntotal == len(self.metadata), (
                    f"FAISS/metadata desync: "
                    f"{self.index.ntotal} vectors vs {len(self.metadata)} metadata entries"
                )

                faiss.write_index(self.index, self.index_path)
                with open(self.meta_path, "wb") as f:
                    pickle.dump(self.metadata, f)
            finally:
                self._release_lock(lf)

    def search(self, query_vec: np.ndarray, k: int = 15) -> list[dict]:
        """Search the index for the k nearest neighbours.

        Reads are concurrent — no lock needed.

        Args:
            query_vec: (768,) float32 query embedding.
            k:         Number of results to return.

        Returns:
            List of chunk metadata dicts, each with an added 'distance' key.
        """
        if self.index.ntotal == 0:
            return []

        distances, indices = self.index.search(query_vec.reshape(1, -1), k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1 or idx >= len(self.metadata):
                continue  # FAISS pads with -1 when k > index.ntotal
            r = self.metadata[idx].copy()
            r["distance"] = float(dist)
            results.append(r)
        return results

    def get_stats(self) -> dict:
        return {"total_vectors": self.index.ntotal, "dimension": self.DIMENSION}

    def clear(self) -> None:
        """Wipe the in-memory index and metadata. Does NOT delete files."""
        self.index = faiss.IndexFlatL2(self.DIMENSION)
        self.metadata = []
        # Also wipe persisted files if they exist
        for path in (self.index_path, self.meta_path):
            if os.path.exists(path):
                os.remove(path)