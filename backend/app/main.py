from __future__ import annotations

import json
import time
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .db import SessionLocal, engine
from .engine import fair_odds_from_probability, implied_probability_from_odds, predict_probability
from .etl import fetch_espn_events
from .migrations import apply_migrations
from .models import BankrollModel, BetModel, EventModel
from .providers import get_provider
from .risk import can_place_stake, max_allowed_stake, recommend_stake
from .schemas import (
    BacktestRequest,
    BacktestResponse,
    BetPlaceRequest,
    BetPlaceResponse,
    BetSettleRequest,
    BetSettleResponse,
    EventIngestRequest,
    PredictRequest,
    PredictResponse,
    StakeRecommendRequest,
    StakeRecommendResponse,
)
from .sport_profile import SPORT_NAME

app = FastAPI(title=f"{SPORT_NAME} Prediction and Betting API", version="0.3.0")

RISK_LIMITS = {
    "min_edge": 0.01,
    "max_stake_fraction": 0.02,
    "max_stake_absolute": 250.0,
    "max_open_exposure_fraction": 0.12,
    "min_confidence": 0.58,
}

apply_migrations(engine)


def now_ms() -> int:
    return int(time.time() * 1000)


def _session():
    return SessionLocal()


def _bankroll_row(db):
    row = db.get(BankrollModel, 1)
    if row is None:
        row = BankrollModel(id=1, currency="USD", starting_balance=10000.0, balance=10000.0)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def _event_to_payload(row: EventModel) -> dict:
    return {
        "event_id": row.event_id,
        "participants": json.loads(row.participants_json),
        "start_time_iso": row.start_time_iso,
        "market_odds_decimal": row.market_odds_decimal,
        "features": json.loads(row.features_json),
        "source": row.source,
        "created_at_ms": row.created_at_ms,
        "updated_at_ms": row.updated_at_ms,
    }


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "sport": SPORT_NAME, "version": "0.3.0"}


@app.get("/", response_class=HTMLResponse)
def ui() -> str:
    return f"""
<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <title>{SPORT_NAME} Betting Console</title>
  <style>
    body {{ font-family: sans-serif; margin: 24px; max-width: 980px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    textarea {{ width: 100%; height: 100px; }}
    input, select, button {{ padding: 6px; margin: 4px 0; }}
    pre {{ background: #f4f4f4; padding: 10px; overflow: auto; }}
    .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 12px; }}
  </style>
</head>
<body>
  <h1>{SPORT_NAME} Betting Console</h1>
  <p>Use this UI to ingest public ESPN events, predict, place, and settle bets.</p>
  <div class=\"grid\">
    <div class=\"card\">
      <h3>Public ETL</h3>
      <button onclick=\"ingestPublic()\">Ingest Latest Public Events</button>
      <button onclick=\"loadEvents()\">Refresh Events</button>
      <pre id=\"events\"></pre>
    </div>
    <div class=\"card\">
      <h3>Predict</h3>
      <input id=\"predictEvent\" placeholder=\"event_id\" />
      <button onclick=\"predictEvent()\">Predict</button>
      <pre id=\"predictOut\"></pre>
    </div>
    <div class=\"card\">
      <h3>Place Bet</h3>
      <input id=\"betEvent\" placeholder=\"event_id\" />
      <input id=\"betSelection\" placeholder=\"selection\" />
      <input id=\"betOdds\" type=\"number\" step=\"0.01\" value=\"1.9\" />
      <input id=\"betStake\" type=\"number\" step=\"0.01\" value=\"20\" />
      <select id=\"betProvider\"><option value=\"paper\">paper</option><option value=\"sportsbook\">sportsbook</option></select>
      <button onclick=\"placeBet()\">Place</button>
      <pre id=\"betOut\"></pre>
    </div>
    <div class=\"card\">
      <h3>Settle Bet</h3>
      <input id=\"settleTicket\" placeholder=\"ticket_id\" />
      <select id=\"settleOutcome\"><option>won</option><option>lost</option><option>push</option></select>
      <button onclick=\"settleBet()\">Settle</button>
      <button onclick=\"loadBankroll()\">Refresh Bankroll</button>
      <pre id=\"bankroll\"></pre>
    </div>
  </div>
<script>
async function j(url, opt={{}}) {{
  const r = await fetch(url, opt);
  const t = await r.text();
  try {{ return JSON.parse(t); }} catch {{ return {{status:r.status, text:t}}; }}
}}
async function ingestPublic() {{
  const out = await j('/etl/public/ingest-latest', {{method:'POST'}});
  document.getElementById('events').textContent = JSON.stringify(out, null, 2);
  await loadEvents();
}}
async function loadEvents() {{
  const out = await j('/events');
  document.getElementById('events').textContent = JSON.stringify(out, null, 2);
}}
async function predictEvent() {{
  const event_id = document.getElementById('predictEvent').value;
  const out = await j('/predict', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body: JSON.stringify({{event_id}})}});
  document.getElementById('predictOut').textContent = JSON.stringify(out, null, 2);
}}
async function placeBet() {{
  const payload = {{
    event_id: document.getElementById('betEvent').value,
    selection: document.getElementById('betSelection').value,
    odds_decimal: Number(document.getElementById('betOdds').value),
    stake_amount: Number(document.getElementById('betStake').value),
    provider: document.getElementById('betProvider').value,
  }};
  const out = await j('/bets/place', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body: JSON.stringify(payload)}});
  document.getElementById('betOut').textContent = JSON.stringify(out, null, 2);
  await loadBankroll();
}}
async function settleBet() {{
  const payload = {{
    ticket_id: document.getElementById('settleTicket').value,
    outcome: document.getElementById('settleOutcome').value,
  }};
  const out = await j('/bets/settle', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body: JSON.stringify(payload)}});
  document.getElementById('betOut').textContent = JSON.stringify(out, null, 2);
  await loadBankroll();
}}
async function loadBankroll() {{
  const out = await j('/bankroll');
  document.getElementById('bankroll').textContent = JSON.stringify(out, null, 2);
}}
loadEvents();
loadBankroll();
</script>
</body>
</html>
"""


@app.post("/events/ingest")
def ingest_event(req: EventIngestRequest) -> dict:
    ts = now_ms()
    with _session() as db:
        row = db.get(EventModel, req.event_id)
        if row is None:
            row = EventModel(
                event_id=req.event_id,
                participants_json=json.dumps(req.participants),
                start_time_iso=req.start_time_iso,
                market_odds_decimal=req.market_odds_decimal,
                features_json=json.dumps(req.features),
                source="manual",
                created_at_ms=ts,
                updated_at_ms=ts,
            )
            db.add(row)
        else:
            row.participants_json = json.dumps(req.participants)
            row.start_time_iso = req.start_time_iso
            row.market_odds_decimal = req.market_odds_decimal
            row.features_json = json.dumps(req.features)
            row.updated_at_ms = ts
        db.commit()
    return {"accepted": True, "event_id": req.event_id}


@app.post("/etl/public/ingest-latest")
def ingest_latest_public_events(limit: int = 20) -> dict:
    events = fetch_espn_events(limit=limit)
    inserted = 0
    updated = 0
    ts = now_ms()

    with _session() as db:
        for ev in events:
            row = db.get(EventModel, ev["event_id"])
            if row is None:
                db.add(
                    EventModel(
                        event_id=ev["event_id"],
                        participants_json=ev["participants_json"],
                        start_time_iso=ev["start_time_iso"],
                        market_odds_decimal=ev["market_odds_decimal"],
                        features_json=ev["features_json"],
                        source=ev["source"],
                        created_at_ms=ts,
                        updated_at_ms=ts,
                    )
                )
                inserted += 1
            else:
                row.participants_json = ev["participants_json"]
                row.start_time_iso = ev["start_time_iso"]
                row.market_odds_decimal = ev["market_odds_decimal"]
                row.features_json = ev["features_json"]
                row.source = ev["source"]
                row.updated_at_ms = ts
                updated += 1
        db.commit()

    return {"fetched": len(events), "inserted": inserted, "updated": updated}


@app.get("/events")
def list_events() -> dict:
    with _session() as db:
        rows = db.query(EventModel).order_by(EventModel.start_time_iso.asc()).all()
        return {"count": len(rows), "events": [_event_to_payload(r) for r in rows]}


@app.get("/events/{event_id}")
def get_event(event_id: str) -> dict:
    with _session() as db:
        row = db.get(EventModel, event_id)
        if row is None:
            raise HTTPException(status_code=404, detail="event not found")
        return _event_to_payload(row)


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    with _session() as db:
        row = db.get(EventModel, req.event_id)
        if row is None:
            raise HTTPException(status_code=404, detail="event not found")
        event = _event_to_payload(row)

    prob, confidence = predict_probability(event["features"])
    implied = implied_probability_from_odds(event["market_odds_decimal"])
    edge = round(prob - implied, 4)
    fair_odds = fair_odds_from_probability(prob)

    return PredictResponse(
        event_id=req.event_id,
        predicted_win_probability=prob,
        implied_market_probability=implied,
        edge=edge,
        fair_odds_decimal=fair_odds,
        confidence=confidence,
        notes="Use /stake/recommend before placing bets.",
    )


@app.post("/stake/recommend", response_model=StakeRecommendResponse)
def stake_recommend(req: StakeRecommendRequest) -> StakeRecommendResponse:
    with _session() as db:
        row = db.get(EventModel, req.event_id)
        if row is None:
            raise HTTPException(status_code=404, detail="event not found")
        event = _event_to_payload(row)
        bankroll = _bankroll_row(db)

    odds = float(req.odds_decimal_override or event["market_odds_decimal"])
    prob, confidence = predict_probability(event["features"])
    implied = implied_probability_from_odds(odds)
    edge = round(prob - implied, 4)

    recommended, reason = recommend_stake(
        balance=float(bankroll.balance),
        prob=prob,
        odds=odds,
        edge=edge,
        confidence=confidence,
        limits=RISK_LIMITS,
    )

    return StakeRecommendResponse(
        event_id=req.event_id,
        recommended_stake=recommended,
        max_allowed_stake=max_allowed_stake(float(bankroll.balance), RISK_LIMITS),
        edge=edge,
        confidence=confidence,
        reason=reason,
    )


@app.post("/bets/place", response_model=BetPlaceResponse)
def place_bet(req: BetPlaceRequest) -> BetPlaceResponse:
    with _session() as db:
        event = db.get(EventModel, req.event_id)
        if event is None:
            raise HTTPException(status_code=404, detail="event not found")

        bankroll = _bankroll_row(db)
        open_bets = db.query(BetModel).filter(BetModel.status == "open").all()

        ok, message = can_place_stake(
            stake=float(req.stake_amount),
            balance=float(bankroll.balance),
            open_bets=[{"stake_amount": b.stake_amount, "status": b.status} for b in open_bets],
            limits=RISK_LIMITS,
        )
        if not ok:
            raise HTTPException(status_code=400, detail=message)

        provider = get_provider(req.provider)
        provider_result = provider.place_bet(req.model_dump())

        if provider_result["accepted"]:
            bankroll.balance = round(float(bankroll.balance) - float(req.stake_amount), 2)
            ticket_id = provider_result["ticket_id"] or f"local-{uuid.uuid4()}"
            db.add(
                BetModel(
                    ticket_id=ticket_id,
                    event_id=req.event_id,
                    selection=req.selection,
                    stake_amount=float(req.stake_amount),
                    odds_decimal=float(req.odds_decimal),
                    provider=req.provider,
                    status="open",
                    outcome=None,
                    payout=0.0,
                    placed_at_ms=now_ms(),
                    settled_at_ms=None,
                )
            )
            db.commit()
        else:
            ticket_id = ""

    return BetPlaceResponse(
        accepted=bool(provider_result["accepted"]),
        ticket_id=ticket_id,
        provider=req.provider,
        event_id=req.event_id,
        selection=req.selection,
        stake_amount=req.stake_amount,
        odds_decimal=req.odds_decimal,
        message=str(provider_result.get("message", "")),
    )


@app.post("/bets/settle", response_model=BetSettleResponse)
def settle_bet(req: BetSettleRequest) -> BetSettleResponse:
    with _session() as db:
        bet = db.get(BetModel, req.ticket_id)
        if bet is None or bet.status != "open":
            raise HTTPException(status_code=404, detail="open ticket not found")

        bankroll = _bankroll_row(db)

        payout = 0.0
        if req.outcome == "won":
            payout = round(float(bet.stake_amount) * float(bet.odds_decimal), 2)
        elif req.outcome == "push":
            payout = round(float(bet.stake_amount), 2)

        bankroll.balance = round(float(bankroll.balance) + payout, 2)
        bet.status = "settled"
        bet.outcome = req.outcome
        bet.payout = payout
        bet.settled_at_ms = now_ms()
        db.commit()

        return BetSettleResponse(
            settled=True,
            ticket_id=req.ticket_id,
            outcome=req.outcome,
            payout=payout,
            new_balance=float(bankroll.balance),
        )


@app.get("/bankroll")
def bankroll() -> dict:
    with _session() as db:
        b = _bankroll_row(db)
        open_bets = db.query(BetModel).filter(BetModel.status == "open").all()
        hist = db.query(BetModel).filter(BetModel.status == "settled").order_by(BetModel.settled_at_ms.desc()).limit(100).all()

        return {
            "currency": b.currency,
            "starting_balance": b.starting_balance,
            "balance": b.balance,
            "open_bets": [
                {
                    "ticket_id": x.ticket_id,
                    "event_id": x.event_id,
                    "selection": x.selection,
                    "stake_amount": x.stake_amount,
                    "odds_decimal": x.odds_decimal,
                }
                for x in open_bets
            ],
            "history": [
                {
                    "ticket_id": x.ticket_id,
                    "event_id": x.event_id,
                    "selection": x.selection,
                    "stake_amount": x.stake_amount,
                    "odds_decimal": x.odds_decimal,
                    "outcome": x.outcome,
                    "payout": x.payout,
                }
                for x in hist
            ],
            "risk_limits": RISK_LIMITS,
        }


@app.get("/stats/performance")
def performance() -> dict:
    with _session() as db:
        settled = db.query(BetModel).filter(BetModel.status == "settled").all()
    if not settled:
        return {"settled_bets": 0, "win_rate": 0.0, "roi": 0.0}

    wins = sum(1 for b in settled if b.outcome == "won")
    total_staked = round(sum(float(b.stake_amount) for b in settled), 2)
    total_payout = round(sum(float(b.payout) for b in settled), 2)
    roi = round((total_payout - total_staked) / total_staked, 4) if total_staked else 0.0

    return {
        "settled_bets": len(settled),
        "win_rate": round(wins / len(settled), 4),
        "total_staked": total_staked,
        "total_payout": total_payout,
        "roi": roi,
    }


@app.post("/simulate/backtest", response_model=BacktestResponse)
def backtest(req: BacktestRequest) -> BacktestResponse:
    total_staked = 0.0
    total_return = 0.0
    wins = 0

    for item in req.items:
        total_staked += item.stake_amount
        if item.won:
            wins += 1
            total_return += item.stake_amount * item.odds_decimal

    roi = (total_return - total_staked) / total_staked if total_staked > 0 else 0.0
    win_rate = wins / len(req.items) if req.items else 0.0

    return BacktestResponse(
        total_staked=round(total_staked, 2),
        total_return=round(total_return, 2),
        roi=round(roi, 4),
        win_rate=round(win_rate, 4),
    )
