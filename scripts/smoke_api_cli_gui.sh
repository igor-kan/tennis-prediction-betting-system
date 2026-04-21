#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${SPORT_API_PORT:-8100}"
BASE_URL="${SPORT_API_BASE_URL:-http://127.0.0.1:${PORT}}"
LOG_FILE="/tmp/$(basename "$ROOT_DIR")-smoke-api.log"

cd "$ROOT_DIR"

if [ ! -d "backend/.venv" ]; then
  python3 -m venv backend/.venv
fi
source backend/.venv/bin/activate
python3 -m pip install -q -r backend/requirements.txt

uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port "$PORT" >"$LOG_FILE" 2>&1 &
API_PID=$!
cleanup() {
  kill "$API_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT
sleep 2

python3 scripts/cli_api.py --base-url "$BASE_URL" health >/dev/null
python3 scripts/cli_api.py --base-url "$BASE_URL" openapi >/dev/null

EVENT_ID="smoke-$(date +%s)"
START_ISO="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

python3 scripts/cli_api.py --base-url "$BASE_URL" ingest-manual \
  --event-id "$EVENT_ID" \
  --participants "Home,Away" \
  --start-time-iso "$START_ISO" \
  --odds 1.91 >/dev/null

python3 scripts/cli_api.py --base-url "$BASE_URL" get-event --event-id "$EVENT_ID" >/dev/null
python3 scripts/cli_api.py --base-url "$BASE_URL" predict --event-id "$EVENT_ID" >/dev/null
python3 scripts/cli_api.py --base-url "$BASE_URL" recommend-stake --event-id "$EVENT_ID" >/dev/null

PLACE_JSON="$(python3 scripts/cli_api.py --base-url "$BASE_URL" place-bet --event-id "$EVENT_ID" --selection Home --odds 1.91 --stake 10 || true)"
TICKET_ID="$(printf '%s' "$PLACE_JSON" | python3 -c 'import json,sys
raw=sys.stdin.read().strip()
if not raw:
 print("")
 raise SystemExit(0)
try:
 obj=json.loads(raw)
except Exception:
 print("")
 raise SystemExit(0)
print(obj.get("ticket_id","") if isinstance(obj,dict) else "")')"
if [ -n "$TICKET_ID" ]; then
  python3 scripts/cli_api.py --base-url "$BASE_URL" settle-bet --ticket-id "$TICKET_ID" --outcome won >/dev/null
fi

rg -q "API Bridge \(Optional\)" docs/index.html

if ! curl -s -D - -o /dev/null -H 'Origin: https://igor-kan.github.io' "$BASE_URL/healthz" | tr -d '\r' | rg -qi '^access-control-allow-origin:'; then
  echo "CORS header check failed"
  exit 1
fi

echo "Smoke check passed for $(basename "$ROOT_DIR")"
