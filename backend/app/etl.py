from __future__ import annotations

import json
from typing import Any

import httpx

from .sport_profile import ESPN_SCOREBOARD_URL


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:  # noqa: BLE001
        return default


def fetch_espn_events(limit: int = 20) -> list[dict]:
    if not ESPN_SCOREBOARD_URL:
        return []

    try:
        with httpx.Client(timeout=20.0) as client:
            resp = client.get(ESPN_SCOREBOARD_URL)
            resp.raise_for_status()
            payload = resp.json()
    except Exception:  # noqa: BLE001
        return []

    events = []
    for ev in payload.get("events", [])[:limit]:
        competitions = ev.get("competitions", [])
        if not competitions:
            continue
        comp = competitions[0]

        competitors = comp.get("competitors", [])
        participants = [c.get("team", {}).get("displayName", "Unknown") for c in competitors]
        participants = [p for p in participants if p]
        if len(participants) < 2:
            continue

        home_adv = 0.25
        if comp.get("neutralSite") is True:
            home_adv = 0.0

        market_odds = 1.91
        odds = comp.get("odds") or []
        if odds and isinstance(odds, list):
            first = odds[0]
            if isinstance(first, dict):
                market_odds = _safe_float(first.get("awayTeamOdds") or first.get("homeTeamOdds"), market_odds)
                if market_odds <= 1.0:
                    market_odds = 1.91

        features = {
            "rating_delta": 0.0,
            "form_delta": 0.0,
            "rest_delta": 0.0,
            "injury_delta": 0.0,
            "market_signal": 0.0,
            "home_advantage": home_adv,
        }

        events.append(
            {
                "event_id": f"espn-{ev.get('id')}",
                "participants_json": json.dumps(participants),
                "start_time_iso": ev.get("date", "1970-01-01T00:00:00Z"),
                "market_odds_decimal": market_odds,
                "features_json": json.dumps(features),
                "source": "espn",
            }
        )

    return events
