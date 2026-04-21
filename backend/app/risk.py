from __future__ import annotations


def open_exposure(open_bets: list[dict]) -> float:
    return round(sum(float(b.get("stake_amount", 0.0)) for b in open_bets if b.get("status") == "open"), 2)


def max_allowed_stake(balance: float, limits: dict) -> float:
    fraction_cap = float(balance) * float(limits["max_stake_fraction"])
    absolute_cap = float(limits["max_stake_absolute"])
    return round(max(0.0, min(fraction_cap, absolute_cap)), 2)


def can_place_stake(stake: float, balance: float, open_bets: list[dict], limits: dict) -> tuple[bool, str]:
    if stake <= 0:
        return False, "stake must be positive"
    if stake > balance:
        return False, "insufficient bankroll"

    allowed = max_allowed_stake(balance, limits)
    if stake > allowed:
        return False, f"stake exceeds per-bet limit ({allowed})"

    current_open = open_exposure(open_bets)
    max_open = round(float(balance) * float(limits["max_open_exposure_fraction"]), 2)
    if current_open + stake > max_open:
        return False, f"stake exceeds open exposure limit ({max_open})"

    return True, "ok"


def recommend_stake(balance: float, prob: float, odds: float, edge: float, confidence: float, limits: dict) -> tuple[float, str]:
    if edge < float(limits["min_edge"]):
        return 0.0, "edge below threshold"
    if confidence < float(limits["min_confidence"]):
        return 0.0, "confidence below threshold"

    b = odds - 1.0
    if b <= 0:
        return 0.0, "invalid odds"

    # Kelly fraction for decimal odds
    kelly = max(0.0, ((odds * prob) - 1.0) / b)
    quarter_kelly = 0.25 * kelly
    raw = round(balance * quarter_kelly, 2)
    capped = min(raw, max_allowed_stake(balance, limits))

    if capped <= 0:
        return 0.0, "no positive stake under risk controls"
    return round(capped, 2), "quarter-kelly capped by risk limits"
