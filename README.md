# SmartAdQuery — Web & Semantic Analytics Engine

An end-to-end semantic analytics platform for ad campaign data: a React
frontend, FastAPI microservices, a FAISS vector index for semantic search,
and a retrieval-augmented generation (RAG) endpoint for natural-language
questions grounded in real campaign metrics.

## Architecture

```
frontend/  React + TypeScript (Vite)
  ├─ Search tab: semantic search over ad copy, "Ask" for RAG-answered questions
  └─ Analytics tab: SQL-backed dashboard (spend, revenue, CTR, ROAS by campaign)

backend/   FastAPI
  ├─ SQLAlchemy + SQLite: ad campaign records (impressions, clicks, spend,
  │  conversions, revenue, ad copy)
  ├─ Embeddings: pluggable backend (TF-IDF by default; swappable for
  │  sentence-transformers) — see app/embeddings.py
  ├─ FAISS: cosine-similarity index over ad-copy embeddings for semantic
  │  search — see app/vector_store.py
  └─ RAG: retrieves top-k relevant ads via FAISS, then generates a grounded
     answer via the Anthropic API if ANTHROPIC_API_KEY is set, otherwise a
     deterministic extractive summary — see app/rag.py
```

## Endpoints

- `GET /api/search?q=...&top_k=5` — semantic search over ad copy
- `POST /api/query` — RAG: `{"question": "...", "top_k": 5}` → grounded answer + sources
- `GET /api/analytics/summary` — SQL aggregates: totals + per-campaign CTR/ROAS
- `GET /api/health`

## Running locally

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

On first startup the app seeds a synthetic dataset of ~300 ad records
(`app/seed_data.py`) and builds the FAISS index automatically.

Optional: set `ANTHROPIC_API_KEY` to enable LLM-generated RAG answers
instead of the extractive fallback.

Run tests:

```bash
cd backend
pytest tests/ -v
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. The Vite dev server proxies `/api` requests
to the backend on port 8000.

## Design notes

- **Embeddings are pluggable.** TF-IDF is the default so the project
  installs and runs in seconds without a large model download; swapping in
  `sentence-transformers` for dense neural embeddings is a one-line config
  change (`EMBEDDING_BACKEND=sentence-transformers`) since both backends
  expose the same `encode()` interface to the FAISS layer.
- **RAG degrades gracefully.** Retrieval (FAISS) always runs; generation
  uses Claude when an API key is configured, and falls back to a
  deterministic extractive summary otherwise — so the endpoint is fully
  functional and testable with zero external dependencies.
- **Metrics (CTR, CPC, ROAS) are computed consistently** in one place
  (`app/metrics.py`) and reused by both the search/RAG responses and the
  analytics dashboard.
