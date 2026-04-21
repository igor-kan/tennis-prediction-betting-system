#!/usr/bin/env python3
"""Curses TUI client for Tennis Prediction and Betting API."""

from __future__ import annotations

import argparse
import curses
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
        try:
            detail = json.loads(raw)
        except json.JSONDecodeError:
            detail = raw
        return {"error": "http_error", "status": exc.code, "detail": detail}
    except URLError as exc:
        return {"error": "network_error", "detail": str(exc)}


def prompt(stdscr: curses.window, message: str) -> str:
    height, _ = stdscr.getmaxyx()
    curses.echo()
    stdscr.addstr(height - 2, 0, " " * 200)
    stdscr.addstr(height - 2, 0, message)
    stdscr.refresh()
    value = stdscr.getstr(height - 2, len(message), 180).decode("utf-8", "replace").strip()
    curses.noecho()
    return value


def draw(stdscr: curses.window, base_url: str, output: str) -> None:
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    title = f"Tennis API TUI  |  base: {base_url}"
    help_line = "h=health i=ingest e=events p=predict r=recommend b=place s=settle k=bankroll f=performance q=quit"

    stdscr.addnstr(0, 0, title, width - 1, curses.A_BOLD)
    stdscr.addnstr(1, 0, help_line, width - 1)
    stdscr.hline(2, 0, ord("-"), width)

    lines = output.splitlines() if output else ["Ready."]
    max_lines = max(1, height - 5)
    visible = lines[-max_lines:]
    for idx, line in enumerate(visible):
        stdscr.addnstr(3 + idx, 0, line, width - 1)

    stdscr.refresh()


def format_output(payload: Any) -> str:
    try:
        return json.dumps(payload, indent=2, sort_keys=True)
    except TypeError:
        return str(payload)


def run_tui(stdscr: curses.window, base_url: str) -> None:
    curses.curs_set(0)
    output = "Ready. Press a key for action."

    while True:
        draw(stdscr, base_url, output)
        key = stdscr.getkey().lower()

        if key == "q":
            break
        if key == "h":
            output = format_output(api_request(base_url, "GET", "/healthz"))
            continue
        if key == "i":
            limit = prompt(stdscr, "limit (default 20): ") or "20"
            output = format_output(api_request(base_url, "POST", "/etl/public/ingest-latest", query={"limit": limit}))
            continue
        if key == "e":
            output = format_output(api_request(base_url, "GET", "/events"))
            continue
        if key == "p":
            event_id = prompt(stdscr, "event_id: ")
            output = format_output(api_request(base_url, "POST", "/predict", payload={"event_id": event_id}))
            continue
        if key == "r":
            event_id = prompt(stdscr, "event_id: ")
            odds_raw = prompt(stdscr, "odds override (optional): ")
            payload: dict[str, Any] = {"event_id": event_id}
            if odds_raw:
                payload["odds_decimal_override"] = float(odds_raw)
            output = format_output(api_request(base_url, "POST", "/stake/recommend", payload=payload))
            continue
        if key == "b":
            event_id = prompt(stdscr, "event_id: ")
            selection = prompt(stdscr, "selection: ")
            odds = float(prompt(stdscr, "odds_decimal: ") or "1.91")
            stake = float(prompt(stdscr, "stake_amount: ") or "20")
            provider = prompt(stdscr, "provider (paper/sportsbook): ") or "paper"
            output = format_output(
                api_request(
                    base_url,
                    "POST",
                    "/bets/place",
                    payload={
                        "event_id": event_id,
                        "selection": selection,
                        "odds_decimal": odds,
                        "stake_amount": stake,
                        "provider": provider,
                    },
                )
            )
            continue
        if key == "s":
            ticket_id = prompt(stdscr, "ticket_id: ")
            outcome = prompt(stdscr, "outcome (won/lost/push): ")
            output = format_output(api_request(base_url, "POST", "/bets/settle", payload={"ticket_id": ticket_id, "outcome": outcome}))
            continue
        if key == "k":
            output = format_output(api_request(base_url, "GET", "/bankroll"))
            continue
        if key == "f":
            output = format_output(api_request(base_url, "GET", "/stats/performance"))
            continue

        output = f"Unknown key: {key}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TUI for Tennis API")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="API base URL (default: %(default)s)")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    curses.wrapper(run_tui, args.base_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
