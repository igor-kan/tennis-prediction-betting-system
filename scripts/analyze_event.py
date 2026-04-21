#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.engine import advanced_breakdown  # noqa: E402


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: analyze_event.py '<json_features>' [market_odds]")

    features = json.loads(sys.argv[1])
    market_odds = float(sys.argv[2]) if len(sys.argv) > 2 else None
    out = advanced_breakdown(features, market_odds=market_odds, simulation_runs=4000)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
