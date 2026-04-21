from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_manual_ingest_predict_place_settle() -> None:
    event_id = "evt-manual-1"

    ingest = client.post(
        "/events/ingest",
        json={
            "event_id": event_id,
            "participants": ["Home", "Away"],
            "start_time_iso": "2026-04-22T19:00:00+00:00",
            "market_odds_decimal": 1.95,
            "features": {
                "rating_delta": 0.6,
                "form_delta": 0.5,
                "rest_delta": 0.3,
                "injury_delta": 0.0,
                "home_advantage": 0.2,
            },
        },
    )
    assert ingest.status_code == 200

    pred = client.post("/predict", json={"event_id": event_id})
    assert pred.status_code == 200

    rec = client.post("/stake/recommend", json={"event_id": event_id})
    assert rec.status_code == 200

    place = client.post(
        "/bets/place",
        json={
            "event_id": event_id,
            "selection": "Home",
            "odds_decimal": 1.95,
            "stake_amount": 20.0,
            "provider": "paper",
        },
    )
    assert place.status_code == 200
    ticket = place.json()["ticket_id"]

    settle = client.post(
        "/bets/settle",
        json={"ticket_id": ticket, "outcome": "won"},
    )
    assert settle.status_code == 200
    assert settle.json()["payout"] > 0

    perf = client.get("/stats/performance")
    assert perf.status_code == 200
    assert perf.json()["settled_bets"] >= 1


def test_public_etl_ingest_endpoint() -> None:
    resp = client.post("/etl/public/ingest-latest?limit=2")
    assert resp.status_code == 200
    body = resp.json()
    assert body["fetched"] >= 0
