#!/usr/bin/env python3
"""Command-line client for Tennis Prediction and Betting API."""

from __future__ import annotations

import argparse
import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = os.getenv("SPORT_API_BASE_URL", "http://127.0.0.1:8100")


def api_request(base_url: str, method: str, path: str, payload: dict[str, Any] | None = None, query: dict[str, Any] | None = None) -> Any:
    url = base_url.rstrip("/") + path
    if query:
        url = f"{url}?{urlencode(query)}"

    headers = {"Accept": "application/json"}
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")

    req = Request(url=url, method=method, headers=headers, data=body)

    try:
        with urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", "replace")
            if not raw:
                return {"ok": True}
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {"raw": raw}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        detail: Any = raw
        try:
            detail = json.loads(raw)
        except json.JSONDecodeError:
            pass
        return {"error": "http_error", "status": exc.code, "detail": detail}
    except URLError as exc:
        return {"error": "network_error", "detail": str(exc)}


def parse_features_json(value: str) -> dict[str, float]:
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("--features-json must decode to an object")
    return {str(k): float(v) for k, v in parsed.items()}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI for Tennis API")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="API base URL (default: %(default)s)")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("health", help="GET /healthz")
    sub.add_parser("openapi", help="GET /openapi.json")

    ingest = sub.add_parser("ingest-public", help="POST /etl/public/ingest-latest")
    ingest.add_argument("--limit", type=int, default=20)

    sub.add_parser("list-events", help="GET /events")

    event = sub.add_parser("get-event", help="GET /events/{event_id}")
    event.add_argument("--event-id", required=True)

    manual = sub.add_parser("ingest-manual", help="POST /events/ingest")
    manual.add_argument("--event-id", required=True)
    manual.add_argument("--participants", required=True, help="Comma-separated values, e.g. Home,Away")
    manual.add_argument("--start-time-iso", required=True, help="ISO timestamp")
    manual.add_argument("--odds", type=float, required=True)
    manual.add_argument(
        "--features-json",
        default='{"rating_delta":0,"form_delta":0,"rest_delta":0,"injury_delta":0,"market_signal":0,"home_advantage":0.25}',
    )

    pred = sub.add_parser("predict", help="POST /predict")
    pred.add_argument("--event-id", required=True)

    rec = sub.add_parser("recommend-stake", help="POST /stake/recommend")
    rec.add_argument("--event-id", required=True)
    rec.add_argument("--odds", type=float, default=None)

    place = sub.add_parser("place-bet", help="POST /bets/place")
    place.add_argument("--event-id", required=True)
    place.add_argument("--selection", required=True)
    place.add_argument("--odds", type=float, required=True)
    place.add_argument("--stake", type=float, required=True)
    place.add_argument("--provider", default="paper")

    settle = sub.add_parser("settle-bet", help="POST /bets/settle")
    settle.add_argument("--ticket-id", required=True)
    settle.add_argument("--outcome", required=True, choices=["won", "lost", "push"])

    sub.add_parser("bankroll", help="GET /bankroll")
    sub.add_parser("performance", help="GET /stats/performance")

    backtest = sub.add_parser("backtest", help="POST /simulate/backtest")
    backtest.add_argument(
        "--items-json",
        required=True,
        help='JSON array like [{"stake_amount":20,"odds_decimal":1.9,"won":true}]',
    )

    return parser


def run(args: argparse.Namespace) -> Any:
    if args.command == "health":
        return api_request(args.base_url, "GET", "/healthz")
    if args.command == "openapi":
        return api_request(args.base_url, "GET", "/openapi.json")
    if args.command == "ingest-public":
        return api_request(args.base_url, "POST", "/etl/public/ingest-latest", query={"limit": args.limit})
    if args.command == "list-events":
        return api_request(args.base_url, "GET", "/events")
    if args.command == "get-event":
        return api_request(args.base_url, "GET", f"/events/{args.event_id}")
    if args.command == "ingest-manual":
        participants = [p.strip() for p in args.participants.split(",") if p.strip()]
        if len(participants) < 2:
            raise ValueError("--participants must include at least two names")
        payload = {
            "event_id": args.event_id,
            "participants": participants,
            "start_time_iso": args.start_time_iso,
            "market_odds_decimal": args.odds,
            "features": parse_features_json(args.features_json),
        }
        return api_request(args.base_url, "POST", "/events/ingest", payload=payload)
    if args.command == "predict":
        return api_request(args.base_url, "POST", "/predict", payload={"event_id": args.event_id})
    if args.command == "recommend-stake":
        payload: dict[str, Any] = {"event_id": args.event_id}
        if args.odds is not None:
            payload["odds_decimal_override"] = args.odds
        return api_request(args.base_url, "POST", "/stake/recommend", payload=payload)
    if args.command == "place-bet":
        return api_request(
            args.base_url,
            "POST",
            "/bets/place",
            payload={
                "event_id": args.event_id,
                "selection": args.selection,
                "odds_decimal": args.odds,
                "stake_amount": args.stake,
                "provider": args.provider,
            },
        )
    if args.command == "settle-bet":
        return api_request(
            args.base_url,
            "POST",
            "/bets/settle",
            payload={"ticket_id": args.ticket_id, "outcome": args.outcome},
        )
    if args.command == "bankroll":
        return api_request(args.base_url, "GET", "/bankroll")
    if args.command == "performance":
        return api_request(args.base_url, "GET", "/stats/performance")
    if args.command == "backtest":
        items = json.loads(args.items_json)
        if not isinstance(items, list):
            raise ValueError("--items-json must decode to a JSON list")
        return api_request(args.base_url, "POST", "/simulate/backtest", payload={"items": items})

    raise ValueError(f"Unknown command: {args.command}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = run(args)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"error": "client_failure", "detail": str(exc)}, indent=2))
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    if isinstance(result, dict) and result.get("error"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
