#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "feature_dataset.csv"


def parse_record_summary(summary: str | None) -> tuple[float, float]:
    if not summary:
        return 0.5, 0.5
    m = re.match(r"\s*(\d+)-(\d+)(?:-(\d+))?", summary)
    if not m:
        return 0.5, 0.5
    wins = int(m.group(1))
    losses = int(m.group(2))
    ties = int(m.group(3) or 0)
    games = wins + losses + ties
    if games <= 0:
        return 0.5, 0.5
    win_pct = (wins + 0.5 * ties) / games
    form_proxy = win_pct
    return win_pct, form_proxy


def get_competitor_record(comp: dict, preferred_name: str) -> tuple[float, float]:
    records = comp.get("records") or []
    if not records:
        return 0.5, 0.5

    preferred = None
    fallback = None
    for r in records:
        name = str(r.get("name", "")).lower()
        summary = r.get("summary")
        if fallback is None and summary:
            fallback = summary
        if preferred_name.lower() in name and summary:
            preferred = summary
            break

    return parse_record_summary(preferred or fallback)


def event_rows(payload: dict) -> list[dict]:
    rows = []
    for ev in payload.get("events", []):
        competitions = ev.get("competitions", [])
        if not competitions:
            continue
        comp = competitions[0]

        competitors = comp.get("competitors", [])
        if len(competitors) < 2:
            continue

        home = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
        away = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])

        home_name = home.get("team", {}).get("displayName", "Home")
        away_name = away.get("team", {}).get("displayName", "Away")

        home_win_pct, home_form = get_competitor_record(home, "overall")
        away_win_pct, away_form = get_competitor_record(away, "overall")

        rating_delta = round(home_win_pct - away_win_pct, 4)
        form_delta = round(home_form - away_form, 4)
        rest_delta = 0.0
        injury_delta = 0.0
        home_advantage = 0.0 if comp.get("neutralSite") else 0.25
        market_signal = 0.0

        odds = comp.get("odds") or []
        market_odds = 1.91
        if odds and isinstance(odds, list) and isinstance(odds[0], dict):
            val = odds[0].get("homeTeamOdds") or odds[0].get("awayTeamOdds")
            try:
                valf = float(val)
                if valf > 1.0:
                    market_odds = valf
            except Exception:  # noqa: BLE001
                pass

        label = ""
        status = ev.get("status", {}).get("type", {}).get("state")
        if status == "post":
            try:
                hs = float(home.get("score", 0))
                as_ = float(away.get("score", 0))
                label = "1" if hs > as_ else "0"
            except Exception:  # noqa: BLE001
                label = ""

        rows.append({
            "event_id": f"espn-{ev.get('id')}",
            "start_time_iso": ev.get("date", ""),
            "home": home_name,
            "away": away_name,
            "market_odds_decimal": market_odds,
            "rating_delta": rating_delta,
            "form_delta": form_delta,
            "rest_delta": rest_delta,
            "injury_delta": injury_delta,
            "market_signal": market_signal,
            "home_advantage": home_advantage,
            "label": label,
        })

    return rows


def main() -> None:
    files = sorted(RAW_DIR.glob("*_scoreboard.json"))
    all_rows = []
    for f in files:
        payload = json.loads(f.read_text(encoding="utf-8"))
        all_rows.extend(event_rows(payload))

    dedup = {}
    for r in all_rows:
        dedup[r["event_id"]] = r
    rows = sorted(dedup.values(), key=lambda x: x["start_time_iso"])

    fieldnames = [
        "event_id",
        "start_time_iso",
        "home",
        "away",
        "market_odds_decimal",
        "rating_delta",
        "form_delta",
        "rest_delta",
        "injury_delta",
        "market_signal",
        "home_advantage",
        "label",
    ]

    with OUT_FILE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)

    labeled = sum(1 for r in rows if str(r["label"]) in {"0", "1"})
    print(json.dumps({
        "rows": len(rows),
        "labeled_rows": labeled,
        "output": str(OUT_FILE),
    }, indent=2))


if __name__ == "__main__":
    main()
