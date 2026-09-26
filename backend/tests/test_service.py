from app.repository import CampaignRepository
from app.service import AnalyticsService


def service() -> AnalyticsService:
    return AnalyticsService(CampaignRepository())


def test_summary_is_grounded() -> None:
    response = service().answer("Give me the portfolio summary")
    assert response.intent == "portfolio_summary"
    assert response.rows[0]["spend"] > 0
    assert response.citations[0].source == "data/campaigns.csv"


def test_channel_comparison_is_sorted_by_roas() -> None:
    response = service().answer("Compare performance by channel")
    assert response.intent == "channel_comparison"
    roas = [row["roas"] for row in response.rows]
    assert roas == sorted(roas, reverse=True)


def test_underperforming_query_uses_safe_template() -> None:
    response = service().answer("Show underperforming campaigns")
    assert response.intent == "underperforming_campaigns"
    assert all(row["roas"] < 2.0 for row in response.rows)

