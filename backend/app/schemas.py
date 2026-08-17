from datetime import date

from pydantic import BaseModel, ConfigDict


class AdOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campaign_name: str
    platform: str
    ad_copy: str
    target_audience: str
    date: date
    impressions: int
    clicks: int
    spend: float
    conversions: int
    revenue: float


class AdMetrics(AdOut):
    ctr: float
    cpc: float
    roas: float


class SearchResult(BaseModel):
    ad: AdMetrics
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


class RagRequest(BaseModel):
    question: str
    top_k: int = 5


class RagResponse(BaseModel):
    question: str
    answer: str
    sources: list[SearchResult]
    generated_by: str  # "llm" | "extractive"


class CampaignSummary(BaseModel):
    campaign_name: str
    platform: str
    impressions: int
    clicks: int
    spend: float
    revenue: float
    ctr: float
    roas: float


class AnalyticsSummary(BaseModel):
    total_spend: float
    total_revenue: float
    total_impressions: int
    total_clicks: int
    overall_ctr: float
    overall_roas: float
    campaigns: list[CampaignSummary]
