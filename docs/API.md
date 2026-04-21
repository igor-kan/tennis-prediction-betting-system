# API

## UI
- `GET /` interactive web console for event ingestion/prediction/betting/settlement.

## Public Data ETL
- `POST /etl/public/ingest-latest?limit=20` ingest latest public ESPN events.

## Event Data
- `POST /events/ingest` ingest manual event payload.
- `GET /events` list persisted events.
- `GET /events/{event_id}` get event details.

## Prediction and Risk
- `POST /predict` model probability and edge.
- `POST /stake/recommend` risk-aware stake recommendation.

## Bet Lifecycle
- `POST /bets/place` place bet.
- `POST /bets/settle` settle ticket.

## Portfolio and Analytics
- `GET /bankroll` bankroll/open/history.
- `GET /stats/performance` settled performance metrics.
- `POST /simulate/backtest` batch ROI simulation.

<!-- API_CLI_TUI_DOCS:START -->
## CLI and TUI Clients

The API can be operated from terminal:
- CLI: `python3 scripts/cli_api.py --help`
- TUI: `python3 scripts/tui_api.py`

Both clients call the same REST endpoints and default to `http://127.0.0.1:8100`.
Override target with:
- `--base-url <url>`
- or `SPORT_API_BASE_URL` environment variable
<!-- API_CLI_TUI_DOCS:END -->
