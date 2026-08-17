import os
import tempfile

import pytest

_tmpdir = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmpdir}/test_ads.db"
os.environ["FAISS_INDEX_PATH"] = f"{_tmpdir}/faiss.index"
os.environ["FAISS_META_PATH"] = f"{_tmpdir}/faiss_meta.json"
os.environ["VECTORIZER_PATH"] = f"{_tmpdir}/tfidf_vectorizer.pkl"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
