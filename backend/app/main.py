from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import Campaign, QueryRequest, QueryResponse
from .repository import CampaignRepository
from .service import AnalyticsService


app = FastAPI(title="SmartAdQuery API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

repository = CampaignRepository()
service = AnalyticsService(repository)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/campaigns", response_model=list[Campaign])
def campaigns() -> list[dict]:
    return repository.execute_template("all")


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    return service.answer(request.question)

