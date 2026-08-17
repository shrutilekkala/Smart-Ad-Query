from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, SessionLocal, engine
from .models import Ad
from .routers import analytics, search
from .seed_data import seed_database
from .vector_store import get_vector_store


def build_index_from_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Ad).count() == 0:
            seed_database()
        ads = db.query(Ad).all()
        store = get_vector_store()
        store.build([ad.id for ad in ads], [ad.ad_copy for ad in ads])
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    build_index_from_db()
    yield


app = FastAPI(title="SmartAdQuery", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(analytics.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
