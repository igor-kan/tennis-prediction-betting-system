#!/usr/bin/env bash
set -euo pipefail
base_url="${1:-http://localhost:8100}"

ingest=$(curl -sS -X POST "$base_url/events/ingest" \
  -H 'Content-Type: application/json' \
  -d '{
    "event_id": "demo-1",
    "participants": ["Home", "Away"],
    "start_time_iso": "2026-04-22T19:00:00+00:00",
    "market_odds_decimal": 1.90,
    "features": {
      "rating_delta": 0.45,
      "form_delta": 0.25,
      "rest_delta": 0.12,
      "injury_delta": 0.03,
      "market_signal": 0.05,
      "home_advantage": 0.20
    }
  }')
echo "$ingest" | jq .

predict=$(curl -sS -X POST "$base_url/predict" -H 'Content-Type: application/json' -d '{"event_id":"demo-1"}')
echo "$predict" | jq .

rec=$(curl -sS -X POST "$base_url/stake/recommend" -H 'Content-Type: application/json' -d '{"event_id":"demo-1"}')
echo "$rec" | jq .

place=$(curl -sS -X POST "$base_url/bets/place" \
  -H 'Content-Type: application/json' \
  -d '{
    "event_id":"demo-1",
    "selection":"Home",
    "odds_decimal":1.90,
    "stake_amount":20,
    "provider":"paper"
  }')
echo "$place" | jq .

ticket=$(echo "$place" | jq -r '.ticket_id')

curl -sS -X POST "$base_url/bets/settle" \
  -H 'Content-Type: application/json' \
  -d "{\"ticket_id\":\"$ticket\",\"outcome\":\"won\"}" | jq .

curl -sS "$base_url/stats/performance" | jq .
curl -sS "$base_url/bankroll" | jq .
