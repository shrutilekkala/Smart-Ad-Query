"""Pluggable text-embedding backends.

Default backend is TF-IDF (via scikit-learn): fast, dependency-light, and
fully deterministic — good for demos/CI without a multi-hundred-MB model
download. Swap EMBEDDING_BACKEND=sentence-transformers for dense neural
embeddings in production; the FAISS index and RAG pipeline are agnostic
to which one is active since both expose the same `encode` interface.
"""
from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .config import EMBEDDING_BACKEND, VECTORIZER_PATH

_VECTORIZER_PATH = Path(VECTORIZER_PATH)


class TfidfEmbedder:
    """TF-IDF vectorizer wrapped to look like a dense embedder.

    FAISS needs fixed-width float32 vectors, so the sparse TF-IDF matrix is
    densified. That's fine at this corpus scale (hundreds-to-low-thousands
    of docs); a neural backend would be swapped in before that stops being
    true.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=512, stop_words="english")
        self._fitted = False

    def fit(self, texts: list[str]) -> np.ndarray:
        matrix = self.vectorizer.fit_transform(texts)
        self._fitted = True
        self._save()
        return matrix.toarray().astype("float32")

    def encode(self, texts: list[str]) -> np.ndarray:
        if not self._fitted:
            self._load()
        matrix = self.vectorizer.transform(texts)
        return matrix.toarray().astype("float32")

    def _save(self) -> None:
        with open(_VECTORIZER_PATH, "wb") as f:
            pickle.dump(self.vectorizer, f)

    def _load(self) -> None:
        if not _VECTORIZER_PATH.exists():
            raise RuntimeError(
                "TF-IDF vectorizer not fitted yet. Build the index first."
            )
        with open(_VECTORIZER_PATH, "rb") as f:
            self.vectorizer = pickle.load(f)
        self._fitted = True

    @property
    def dim(self) -> int:
        return len(self.vectorizer.vocabulary_)


class SentenceTransformerEmbedder:
    """Optional dense-embedding backend. Requires `sentence-transformers`."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer  # lazy import

        self.model = SentenceTransformer(model_name)

    def fit(self, texts: list[str]) -> np.ndarray:
        return self.encode(texts)

    def encode(self, texts: list[str]) -> np.ndarray:
        return np.asarray(self.model.encode(texts), dtype="float32")

    @property
    def dim(self) -> int:
        return self.model.get_sentence_embedding_dimension()


def get_embedder():
    if EMBEDDING_BACKEND == "sentence-transformers":
        return SentenceTransformerEmbedder()
    return TfidfEmbedder()
