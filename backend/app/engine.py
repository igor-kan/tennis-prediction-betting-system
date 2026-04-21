from __future__ import annotations

import json
import math
import random
import statistics
from functools import lru_cache
from pathlib import Path

from .sport_profile import FEATURE_WEIGHTS, MODEL_CONFIDENCE_FLOOR


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _logit(p: float) -> float:
    p = _clamp(p, 1e-6, 1 - 1e-6)
    return math.log(p / (1 - p))


def implied_probability_from_odds(odds_decimal: float) -> float:
    return round(1.0 / odds_decimal, 4)


def fair_odds_from_probability(prob: float) -> float:
    prob = _clamp(prob, 0.01, 0.99)
    return round(1.0 / prob, 4)


@lru_cache(maxsize=1)
def _load_calibration_params() -> dict:
    path = Path(__file__).resolve().parents[2] / "data" / "models" / "calibration.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        a = float(payload.get("a", 1.0))
        b = float(payload.get("b", 0.0))
        return {"a": a, "b": b}
    except Exception:  # noqa: BLE001
        return {}


def _apply_calibration(prob: float) -> float:
    params = _load_calibration_params()
    if not params:
        return prob
    a = params["a"]
    b = params["b"]
    z = a * _logit(prob) + b
    return _clamp(_sigmoid(z), 0.01, 0.99)


def _feature_vector(features: dict[str, float]) -> dict[str, float]:
    vec: dict[str, float] = {}
    for k in FEATURE_WEIGHTS:
        vec[k] = float(features.get(k, 0.0))
    return vec


def _linear_model_prob(vec: dict[str, float]) -> float:
    score = sum(FEATURE_WEIGHTS[k] * vec[k] for k in FEATURE_WEIGHTS)
    return _clamp(_sigmoid(score / 2.2), 0.01, 0.99)


def _nonlinear_model_prob(vec: dict[str, float]) -> float:
    rating = vec.get("rating_delta", 0.0)
    form = vec.get("form_delta", 0.0)
    rest = vec.get("rest_delta", 0.0)
    injury = vec.get("injury_delta", 0.0)
    home = vec.get("home_advantage", 0.0)

    base = sum(FEATURE_WEIGHTS[k] * vec[k] for k in FEATURE_WEIGHTS)
    interaction = 0.9 * rating * form + 0.45 * rest * home - 0.8 * injury * abs(form)
    saturation = 0.7 * math.tanh(rating) + 0.6 * math.tanh(form) + 0.25 * math.tanh(home)
    score = 0.5 * base + interaction + saturation
    return _clamp(_sigmoid(score / 2.0), 0.01, 0.99)


def _momentum_model_prob(vec: dict[str, float]) -> float:
    score = (
        1.2 * vec.get("form_delta", 0.0)
        + 0.85 * vec.get("rating_delta", 0.0)
        + 0.35 * vec.get("home_advantage", 0.0)
        - 0.7 * vec.get("injury_delta", 0.0)
        + 0.25 * vec.get("rest_delta", 0.0)
    )
    return _clamp(_sigmoid(score), 0.01, 0.99)


def deterministic_breakdown(features: dict[str, float], market_odds: float | None = None) -> dict:
    vec = _feature_vector(features)

    linear_prob = _linear_model_prob(vec)
    nonlinear_prob = _nonlinear_model_prob(vec)
    momentum_prob = _momentum_model_prob(vec)

    component_probs = {
        "linear": linear_prob,
        "nonlinear": nonlinear_prob,
        "momentum": momentum_prob,
    }

    if market_odds and market_odds > 1.0:
        market_prob = implied_probability_from_odds(market_odds)
        component_probs["market"] = market_prob
        weights = {"linear": 0.3, "nonlinear": 0.3, "momentum": 0.2, "market": 0.2}
    else:
        market_prob = None
        weights = {"linear": 0.4, "nonlinear": 0.35, "momentum": 0.25}

    ensemble_prob = 0.0
    for name, prob in component_probs.items():
        ensemble_prob += weights.get(name, 0.0) * prob

    values = list(component_probs.values())
    consensus_std = statistics.pstdev(values) if len(values) > 1 else 0.0

    if market_prob is not None:
        edge = ensemble_prob - market_prob
    else:
        edge = ensemble_prob - 0.5

    present = sum(1 for k in FEATURE_WEIGHTS if k in features)
    coverage = present / max(1, len(FEATURE_WEIGHTS))
    consensus_score = _clamp(1.0 - (2.2 * consensus_std), 0.0, 1.0)
    edge_score = _clamp(abs(edge) * 4.0, 0.0, 1.0)

    confidence = 0.45 + 0.25 * coverage + 0.2 * consensus_score + 0.1 * edge_score + (0.05 if market_prob is not None else 0.0)
    confidence = _clamp(confidence, MODEL_CONFIDENCE_FLOOR, 0.97)

    calibrated_prob = _apply_calibration(_clamp(ensemble_prob, 0.01, 0.99))

    return {
        "probability": round(calibrated_prob, 4),
        "confidence": round(confidence, 4),
        "edge": round(edge, 4),
        "consensus_std": round(consensus_std, 4),
        "components": {k: round(v, 4) for k, v in component_probs.items()},
    }


def advanced_breakdown(features: dict[str, float], market_odds: float | None = None, simulation_runs: int = 3000) -> dict:
    base = deterministic_breakdown(features, market_odds)

    mean_prob = float(base["probability"])
    confidence = float(base["confidence"])
    consensus_std = float(base["consensus_std"])

    sigma = max(0.015, consensus_std * 0.7 + (1.0 - confidence) * 0.2)
    samples = [_clamp(random.gauss(mean_prob, sigma), 0.01, 0.99) for _ in range(max(200, simulation_runs))]
    samples.sort()

    def q(p: float) -> float:
        idx = int(p * (len(samples) - 1))
        return round(samples[idx], 4)

    out = {
        **base,
        "simulation": {
            "runs": len(samples),
            "prob_q10": q(0.1),
            "prob_q50": q(0.5),
            "prob_q90": q(0.9),
            "prob_mean": round(statistics.fmean(samples), 4),
            "prob_std": round(statistics.pstdev(samples), 4),
        },
    }

    if market_odds and market_odds > 1.0:
        implied = implied_probability_from_odds(market_odds)
        edge_samples = [p - implied for p in samples]
        ev_samples = [(p * (market_odds - 1.0)) - (1.0 - p) for p in samples]
        edge_samples_sorted = sorted(edge_samples)
        ev_samples_sorted = sorted(ev_samples)
        out["market_analysis"] = {
            "implied_probability": implied,
            "edge_mean": round(statistics.fmean(edge_samples), 4),
            "edge_q10": round(edge_samples_sorted[int(0.1 * (len(edge_samples_sorted) - 1))], 4),
            "edge_q90": round(edge_samples_sorted[int(0.9 * (len(edge_samples_sorted) - 1))], 4),
            "ev_mean_per_unit": round(statistics.fmean(ev_samples), 4),
            "ev_q10_per_unit": round(ev_samples_sorted[int(0.1 * (len(ev_samples_sorted) - 1))], 4),
            "ev_q90_per_unit": round(ev_samples_sorted[int(0.9 * (len(ev_samples_sorted) - 1))], 4),
            "positive_ev_probability": round(sum(1 for v in ev_samples if v > 0) / len(ev_samples), 4),
        }

    return out


def predict_probability(features: dict[str, float]) -> tuple[float, float]:
    out = deterministic_breakdown(features, market_odds=None)
    return out["probability"], out["confidence"]
