from .models import Ad


def ctr(impressions: int, clicks: int) -> float:
    return round(clicks / impressions, 4) if impressions else 0.0


def cpc(clicks: int, spend: float) -> float:
    return round(spend / clicks, 4) if clicks else 0.0


def roas(spend: float, revenue: float) -> float:
    return round(revenue / spend, 4) if spend else 0.0


def ad_to_metrics_dict(ad: Ad) -> dict:
    return {
        "id": ad.id,
        "campaign_name": ad.campaign_name,
        "platform": ad.platform,
        "ad_copy": ad.ad_copy,
        "target_audience": ad.target_audience,
        "date": ad.date,
        "impressions": ad.impressions,
        "clicks": ad.clicks,
        "spend": ad.spend,
        "conversions": ad.conversions,
        "revenue": ad.revenue,
        "ctr": ctr(ad.impressions, ad.clicks),
        "cpc": cpc(ad.clicks, ad.spend),
        "roas": roas(ad.spend, ad.revenue),
    }
