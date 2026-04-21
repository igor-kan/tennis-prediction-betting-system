#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.engine import predict_probability  # noqa: E402

DATASET = ROOT / "data" / "processed" / "feature_dataset.csv"
OUT_DIR = ROOT / "data" / "models"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "calibration.json"


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def logit(p: float) -> float:
    p = clamp(p, 1e-6, 1 - 1e-6)
    return math.log(p / (1 - p))


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def main() -> None:
    if not DATASET.exists():
        raise SystemExit(f"dataset not found: {DATASET}")

    xs = []
    ys = []

    with DATASET.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = row.get("label", "")
            if label not in {"0", "1"}:
                continue
            features = {
                "rating_delta": float(row.get("rating_delta", 0.0)),
                "form_delta": float(row.get("form_delta", 0.0)),
                "rest_delta": float(row.get("rest_delta", 0.0)),
                "injury_delta": float(row.get("injury_delta", 0.0)),
                "market_signal": float(row.get("market_signal", 0.0)),
                "home_advantage": float(row.get("home_advantage", 0.0)),
            }
            p, _ = predict_probability(features)
            xs.append(logit(p))
            ys.append(float(label))

    n = len(xs)
    if n < 20:
        print(json.dumps({"trained": False, "reason": "insufficient labeled rows", "rows": n}, indent=2))
        return

    a = 1.0
    b = 0.0
    lr = 0.03

    for _ in range(800):
        da = 0.0
        db = 0.0
        for x, y in zip(xs, ys):
            p = sigmoid(a * x + b)
            err = p - y
            da += err * x
            db += err
        a -= lr * (da / n)
        b -= lr * (db / n)

    payload = {
        "a": round(a, 6),
        "b": round(b, 6),
        "trained_samples": n,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    OUT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps({"trained": True, "output": str(OUT_FILE), **payload}, indent=2))


if __name__ == "__main__":
    main()
