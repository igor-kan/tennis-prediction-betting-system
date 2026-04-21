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
