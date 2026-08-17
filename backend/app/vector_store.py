"""FAISS-backed semantic index over ad copy."""
from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np

from .config import FAISS_INDEX_PATH, FAISS_META_PATH
from .embeddings import get_embedder


def _normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms


class VectorStore:
    def __init__(self):
        self.embedder = get_embedder()
        self.index: faiss.Index | None = None
        self.ad_ids: list[int] = []

    def build(self, ad_ids: list[int], texts: list[str]) -> None:
        vectors = self.embedder.fit(texts)
        vectors = _normalize(vectors)
        dim = vectors.shape[1]
        # inner product on normalized vectors == cosine similarity
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(vectors)
        self.ad_ids = ad_ids
        self._save()

    def search(self, query: str, top_k: int = 5) -> list[tuple[int, float]]:
        if self.index is None:
            self._load()
        query_vec = _normalize(self.embedder.encode([query]))
        scores, indices = self.index.search(query_vec, min(top_k, len(self.ad_ids)))
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx == -1:
                continue
            results.append((self.ad_ids[idx], float(score)))
        return results

    def _save(self) -> None:
        faiss.write_index(self.index, FAISS_INDEX_PATH)
        with open(FAISS_META_PATH, "w") as f:
            json.dump({"ad_ids": self.ad_ids}, f)

    def _load(self) -> None:
        if not Path(FAISS_INDEX_PATH).exists():
            raise RuntimeError("FAISS index not built yet. Call build() first.")
        self.index = faiss.read_index(FAISS_INDEX_PATH)
        with open(FAISS_META_PATH) as f:
            self.ad_ids = json.load(f)["ad_ids"]


_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
        try:
            _store._load()
        except RuntimeError:
            pass  # not built yet; caller should build() during startup/seed
    return _store
