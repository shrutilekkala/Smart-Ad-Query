from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_contract() -> None:
    response = client.post("/query", json={"question": "Show the top campaigns"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "top_campaigns"
    assert payload["rows"]
    assert payload["citations"][0]["source"] == "data/campaigns.csv"
