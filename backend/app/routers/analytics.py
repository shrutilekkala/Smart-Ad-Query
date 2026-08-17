from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..metrics import ctr, roas
from ..models import Ad
from ..schemas import AnalyticsSummary, CampaignSummary

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def analytics_summary(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Ad.campaign_name,
            Ad.platform,
            func.sum(Ad.impressions).label("impressions"),
            func.sum(Ad.clicks).label("clicks"),
            func.sum(Ad.spend).label("spend"),
            func.sum(Ad.revenue).label("revenue"),
        )
        .group_by(Ad.campaign_name, Ad.platform)
        .order_by(func.sum(Ad.revenue).desc())
        .all()
    )

    campaigns = [
        CampaignSummary(
            campaign_name=r.campaign_name,
            platform=r.platform,
            impressions=r.impressions,
            clicks=r.clicks,
            spend=round(r.spend, 2),
            revenue=round(r.revenue, 2),
            ctr=ctr(r.impressions, r.clicks),
            roas=roas(r.spend, r.revenue),
        )
        for r in rows
    ]

    totals = db.query(
        func.sum(Ad.impressions),
        func.sum(Ad.clicks),
        func.sum(Ad.spend),
        func.sum(Ad.revenue),
    ).first()
    total_impressions, total_clicks, total_spend, total_revenue = (
        totals[0] or 0,
        totals[1] or 0,
        totals[2] or 0.0,
        totals[3] or 0.0,
    )

    return AnalyticsSummary(
        total_spend=round(total_spend, 2),
        total_revenue=round(total_revenue, 2),
        total_impressions=total_impressions,
        total_clicks=total_clicks,
        overall_ctr=ctr(total_impressions, total_clicks),
        overall_roas=roas(total_spend, total_revenue),
        campaigns=campaigns,
    )
