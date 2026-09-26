import math
import re
from collections import Counter


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> Counter[str]:
    return Counter(TOKEN_PATTERN.findall(text.lower()))


def cosine(left: Counter[str], right: Counter[str]) -> float:
    numerator = sum(value * right.get(key, 0) for key, value in left.items())
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0


class SemanticRetriever:
    """Deterministic local retrieval for campaign metadata; no external model required."""

    def __init__(self, records: list[dict]) -> None:
        self.records = records
        self.vectors = [tokenize(self._document(record)) for record in records]

    @staticmethod
    def _document(record: dict) -> str:
        return " ".join(
            str(record.get(field, ""))
            for field in ("campaign_id", "campaign_name", "channel", "region")
        )

    def search(self, query: str, limit: int = 3) -> list[dict]:
        query_vector = tokenize(query)
        ranked = sorted(
            zip(self.records, self.vectors),
            key=lambda item: cosine(query_vector, item[1]),
            reverse=True,
        )
        return [record for record, vector in ranked[:limit] if cosine(query_vector, vector) > 0]

