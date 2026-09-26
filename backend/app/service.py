from .models import Citation, QueryResponse
from .repository import CampaignRepository
from .retrieval import SemanticRetriever


class AnalyticsService:
    def __init__(self, repository: CampaignRepository) -> None:
        self.repository = repository
        self.retriever = SemanticRetriever(repository.execute_template("all"))

    def answer(self, question: str) -> QueryResponse:
        normalized = question.lower()
        limitations = [
            "Results use a synthetic dataset.",
            "Intent selection is deterministic and does not generate arbitrary SQL.",
        ]

        if any(term in normalized for term in ("underperform", "low roas", "below")):
            rows = self.repository.execute_template("underperforming", (2.0,))
            intent = "underperforming_campaigns"
            answer = f"Found {len(rows)} campaigns with ROAS below 2.0."
        elif any(term in normalized for term in ("channel", "compare", "platform")):
            rows = self.repository.execute_template("channel")
            intent = "channel_comparison"
            leader = rows[0] if rows else None
            answer = (
                f"{leader['channel']} leads channel performance at {leader['roas']} ROAS."
                if leader
                else "No channel data is available."
            )
        elif any(term in normalized for term in ("top", "best", "highest")):
            rows = self.repository.execute_template("top", (5,))
            intent = "top_campaigns"
            answer = (
                f"{rows[0]['campaign_name']} has the highest ROAS at {rows[0]['roas']}."
                if rows
                else "No campaign data is available."
            )
        else:
            semantic_rows = self.retriever.search(question)
            if semantic_rows:
                rows = semantic_rows
                intent = "semantic_campaign_lookup"
                answer = f"Found {len(rows)} campaigns related to the question."
            else:
                rows = self.repository.execute_template("summary")
                intent = "portfolio_summary"
                summary = rows[0]
                answer = (
                    f"The portfolio generated ${summary['revenue']:,.0f} in revenue "
                    f"from ${summary['spend']:,.0f} in spend ({summary['roas']} ROAS)."
                )

        ids = [str(row["campaign_id"]) for row in rows if "campaign_id" in row]
        return QueryResponse(
            answer=answer,
            intent=intent,
            rows=rows,
            citations=[Citation(source="data/campaigns.csv", record_ids=ids)],
            confidence="high" if intent != "semantic_campaign_lookup" else "medium",
            limitations=limitations,
        )

