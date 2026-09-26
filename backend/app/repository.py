import csv
import sqlite3
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "campaigns.csv"


class CampaignRepository:
    """Read-only analytics repository backed by an in-memory SQLite database."""

    def __init__(self, data_path: Path = DATA_PATH) -> None:
        self.connection = sqlite3.connect(":memory:", check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._load(data_path)

    def _load(self, data_path: Path) -> None:
        self.connection.execute(
            """
            CREATE TABLE campaigns (
                campaign_id TEXT PRIMARY KEY,
                campaign_name TEXT NOT NULL,
                channel TEXT NOT NULL,
                region TEXT NOT NULL,
                spend REAL NOT NULL CHECK (spend >= 0),
                impressions INTEGER NOT NULL CHECK (impressions >= 0),
                clicks INTEGER NOT NULL CHECK (clicks >= 0),
                conversions INTEGER NOT NULL CHECK (conversions >= 0),
                revenue REAL NOT NULL CHECK (revenue >= 0)
            )
            """
        )
        with data_path.open(newline="", encoding="utf-8") as stream:
            records = list(csv.DictReader(stream))
        self.connection.executemany(
            """
            INSERT INTO campaigns VALUES (
                :campaign_id, :campaign_name, :channel, :region,
                :spend, :impressions, :clicks, :conversions, :revenue
            )
            """,
            records,
        )
        self.connection.commit()

    def execute_template(self, template: str, params: tuple = ()) -> list[dict]:
        allowed = {
            "summary": """
                SELECT ROUND(SUM(spend), 2) AS spend,
                       SUM(impressions) AS impressions,
                       SUM(clicks) AS clicks,
                       SUM(conversions) AS conversions,
                       ROUND(SUM(revenue), 2) AS revenue,
                       ROUND(SUM(revenue) / NULLIF(SUM(spend), 0), 2) AS roas
                FROM campaigns
            """,
            "channel": """
                SELECT channel, ROUND(SUM(spend), 2) AS spend,
                       SUM(conversions) AS conversions,
                       ROUND(SUM(revenue), 2) AS revenue,
                       ROUND(SUM(revenue) / NULLIF(SUM(spend), 0), 2) AS roas
                FROM campaigns GROUP BY channel ORDER BY roas DESC
            """,
            "top": """
                SELECT campaign_id, campaign_name, channel,
                       ROUND(spend, 2) AS spend, conversions,
                       ROUND(revenue, 2) AS revenue,
                       ROUND(revenue / NULLIF(spend, 0), 2) AS roas
                FROM campaigns ORDER BY roas DESC LIMIT ?
            """,
            "underperforming": """
                SELECT campaign_id, campaign_name, channel,
                       ROUND(spend, 2) AS spend, conversions,
                       ROUND(revenue, 2) AS revenue,
                       ROUND(revenue / NULLIF(spend, 0), 2) AS roas
                FROM campaigns WHERE revenue / NULLIF(spend, 0) < ?
                ORDER BY roas ASC
            """,
            "all": "SELECT * FROM campaigns ORDER BY campaign_id",
        }
        if template not in allowed:
            raise ValueError("Unknown query template")
        return [dict(row) for row in self.connection.execute(allowed[template], params)]

