from typing import Literal

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class Citation(BaseModel):
    source: str
    record_ids: list[str]


class QueryResponse(BaseModel):
    answer: str
    intent: str
    rows: list[dict[str, str | int | float]]
    citations: list[Citation]
    confidence: Literal["high", "medium", "low"]
    limitations: list[str]


class Campaign(BaseModel):
    campaign_id: str
    campaign_name: str
    channel: str
    region: str
    spend: float
    impressions: int
    clicks: int
    conversions: int
    revenue: float

