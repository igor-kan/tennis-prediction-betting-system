#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import sys

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.sport_profile import ESPN_SCOREBOARD_URL, SPORT_NAME  # noqa: E402


def main() -> None:
    out_dir = ROOT / "data" / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    with httpx.Client(timeout=20.0) as client:
        resp = client.get(ESPN_SCOREBOARD_URL)
        resp.raise_for_status()
        payload = resp.json()

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_file = out_dir / f"{ts}_scoreboard.json"
    out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    events = payload.get("events", [])
    print(json.dumps({
        "sport": SPORT_NAME,
        "source": ESPN_SCOREBOARD_URL,
        "saved_file": str(out_file),
        "events": len(events),
    }, indent=2))


if __name__ == "__main__":
    main()
