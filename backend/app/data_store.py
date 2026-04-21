from __future__ import annotations

EVENTS: dict[str, dict] = {}
BANKROLL = {
    "currency": "USD",
    "starting_balance": 10000.0,
    "balance": 10000.0,
    "open_bets": [],
    "history": [],
}
RISK_LIMITS = {
    "min_edge": 0.01,
    "max_stake_fraction": 0.02,
    "max_stake_absolute": 250.0,
    "max_open_exposure_fraction": 0.12,
    "min_confidence": 0.58,
}
