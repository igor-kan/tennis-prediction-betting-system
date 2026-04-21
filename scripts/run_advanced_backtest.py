#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.engine import advanced_breakdown  # noqa: E402

DATASET = ROOT / "data" / "processed" / "feature_dataset.csv"
REPORT_DIR = ROOT / "data" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def log_loss(y: int, p: float) -> float:
    p = clamp(p, 1e-6, 1 - 1e-6)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def bootstrap_roi(returns: list[float], rounds: int = 1000) -> tuple[float, float]:
    if not returns:
        return 0.0, 0.0
    rois = []
    n = len(returns)
    for _ in range(rounds):
        sample = [returns[random.randrange(n)] for _ in range(n)]
        rois.append(sum(sample) / n)
    rois.sort()
    return rois[int(0.05 * (len(rois) - 1))], rois[int(0.95 * (len(rois) - 1))]


def main() -> None:
    if not DATASET.exists():
        raise SystemExit(f"dataset not found: {DATASET}")

    rows = []
    with DATASET.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("label") not in {"0", "1"}:
                continue
            rows.append(row)

    if not rows:
        print(json.dumps({"ok": False, "reason": "no labeled rows"}, indent=2))
        return

    brier_sum = 0.0
    logloss_sum = 0.0
    bets = 0
    wins = 0
    pnl = 0.0
    returns = []
    running = 0.0
    peak = 0.0
    max_drawdown = 0.0

    bucket = {str(i): {"count": 0, "avg_p": 0.0, "avg_y": 0.0} for i in range(10)}

    for row in rows:
        y = int(row["label"])
        odds = float(row.get("market_odds_decimal", 1.91))
        features = {
            "rating_delta": float(row.get("rating_delta", 0.0)),
            "form_delta": float(row.get("form_delta", 0.0)),
            "rest_delta": float(row.get("rest_delta", 0.0)),
            "injury_delta": float(row.get("injury_delta", 0.0)),
            "market_signal": float(row.get("market_signal", 0.0)),
            "home_advantage": float(row.get("home_advantage", 0.0)),
        }

        out = advanced_breakdown(features, market_odds=odds, simulation_runs=500)
        p = float(out["probability"])
        c = float(out["confidence"])
        edge = float(out["edge"])

        brier_sum += (p - y) ** 2
        logloss_sum += log_loss(y, p)

        idx = min(9, int(p * 10))
        b = bucket[str(idx)]
        b["count"] += 1
        b["avg_p"] += p
        b["avg_y"] += y

        # Policy: bet 1 unit when edge and confidence clear thresholds.
        if edge >= 0.02 and c >= 0.62:
            bets += 1
            r = (odds - 1.0) if y == 1 else -1.0
            returns.append(r)
            pnl += r
            if y == 1:
                wins += 1

            running += r
            peak = max(peak, running)
            dd = peak - running
            max_drawdown = max(max_drawdown, dd)

    n = len(rows)
    for v in bucket.values():
        if v["count"] > 0:
            v["avg_p"] = round(v["avg_p"] / v["count"], 4)
            v["avg_y"] = round(v["avg_y"] / v["count"], 4)

    roi_per_bet = (pnl / bets) if bets > 0 else 0.0
    roi_ci_low, roi_ci_high = bootstrap_roi(returns, rounds=1000)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rows": n,
        "brier": round(brier_sum / n, 5),
        "log_loss": round(logloss_sum / n, 5),
        "policy": {
            "edge_threshold": 0.02,
            "confidence_threshold": 0.62,
            "stake_units": 1.0,
        },
        "bets": bets,
        "wins": wins,
        "win_rate": round((wins / bets) if bets > 0 else 0.0, 4),
        "roi_per_bet": round(roi_per_bet, 4),
        "roi_bootstrap_ci_90": [round(roi_ci_low, 4), round(roi_ci_high, 4)],
        "max_drawdown_units": round(max_drawdown, 4),
        "calibration_buckets": bucket,
    }

    out_file = REPORT_DIR / f"advanced_backtest_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    out_file.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({"ok": True, "report": str(out_file), **report}, indent=2))


if __name__ == "__main__":
    main()
