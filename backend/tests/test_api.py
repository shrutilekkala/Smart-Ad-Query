def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_semantic_search_returns_relevant_results(client):
    resp = client.get("/api/search", params={"q": "sneakers for young shoppers", "top_k": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert body["query"] == "sneakers for young shoppers"
    assert len(body["results"]) > 0
    top = body["results"][0]
    assert "ad" in top and "score" in top
    assert top["ad"]["ctr"] >= 0


def test_search_results_are_score_ordered(client):
    resp = client.get("/api/search", params={"q": "laptop deals for students", "top_k": 10})
    scores = [r["score"] for r in resp.json()["results"]]
    assert scores == sorted(scores, reverse=True)


def test_rag_query_falls_back_to_extractive_without_api_key(client):
    resp = client.post("/api/query", json={"question": "which ad performs best for pet owners?", "top_k": 3})
    assert resp.status_code == 200
    body = resp.json()
    assert body["generated_by"] == "extractive"
    assert len(body["answer"]) > 0
    assert len(body["sources"]) > 0


def test_analytics_summary(client):
    resp = client.get("/api/analytics/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_impressions"] > 0
    assert body["total_clicks"] > 0
    assert len(body["campaigns"]) > 0
    assert 0 <= body["overall_ctr"] <= 1
