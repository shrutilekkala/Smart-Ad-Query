import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'ads.db'}")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", str(DATA_DIR / "faiss.index"))
FAISS_META_PATH = os.getenv("FAISS_META_PATH", str(DATA_DIR / "faiss_meta.json"))
VECTORIZER_PATH = os.getenv("VECTORIZER_PATH", str(DATA_DIR / "tfidf_vectorizer.pkl"))

EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "tfidf")  # "tfidf" | "sentence-transformers"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
