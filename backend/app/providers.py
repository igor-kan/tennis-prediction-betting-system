from __future__ import annotations

import os
import uuid
import httpx


class PaperBetProvider:
    name = "paper"

    def place_bet(self, payload: dict) -> dict:
        return {
            "accepted": True,
            "ticket_id": f"paper-{uuid.uuid4()}",
            "message": "Paper bet accepted",
        }


class SportsbookHTTPProvider:
    name = "sportsbook"

    def place_bet(self, payload: dict) -> dict:
        if os.getenv("ALLOW_LIVE_BETTING", "false").lower() != "true":
            return {
                "accepted": False,
                "ticket_id": "",
                "message": "Live betting disabled. Set ALLOW_LIVE_BETTING=true to enable.",
            }

        api_base = os.getenv("SPORTSBOOK_API_BASE_URL")
        api_key = os.getenv("SPORTSBOOK_API_KEY")
        if not api_base or not api_key:
            return {
                "accepted": False,
                "ticket_id": "",
                "message": "Missing SPORTSBOOK_API_BASE_URL or SPORTSBOOK_API_KEY",
            }

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    f"{api_base.rstrip('/')}/bets",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json=payload,
                )
            if resp.status_code >= 300:
                return {
                    "accepted": False,
                    "ticket_id": "",
                    "message": f"Sportsbook API rejected request: {resp.status_code}",
                }
            body = resp.json() if resp.content else {}
            return {
                "accepted": True,
                "ticket_id": str(body.get("ticket_id", uuid.uuid4())),
                "message": "Live bet accepted",
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "accepted": False,
                "ticket_id": "",
                "message": f"Sportsbook API error: {exc}",
            }


def get_provider(name: str):
    if name == "paper":
        return PaperBetProvider()
    if name == "sportsbook":
        return SportsbookHTTPProvider()
    raise ValueError(f"Unknown provider: {name}")
