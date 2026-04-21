# Tennis Prediction and Betting System

Repository for Tennis outcome prediction and betting workflows using publicly available data.

## What's Implemented (v3)
- Public ETL connector (ESPN scoreboard ingest endpoint)
- Persistent storage with SQLite + migrations
- Risk-aware stake recommendation
- Bet placement and settlement lifecycle
- Bankroll and performance tracking
- Web UI for ingest/predict/place/settle (`GET /`)

## Quick Start

a) Start backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8100
```

b) Open UI
- http://localhost:8100/

c) Optional: run migrations manually
```bash
./scripts/migrate.sh
```

## Important Files
- `backend/app/main.py`
- `backend/app/etl.py`
- `backend/app/models.py`
- `backend/migrations/001_init.sql`
- `docs/API.md`

<!-- ADVANCED_PIPELINE:START -->
## Advanced Analysis Pipeline

- Algorithms and methodology: `docs/ADVANCED_MODELING.md`
- Run full pipeline:
```bash
./scripts/run_advanced_pipeline.sh
```
- Analyze one event feature payload manually:
```bash
python3 scripts/analyze_event.py '{"rating_delta":0.4,"form_delta":0.2,"rest_delta":0.1,"injury_delta":0.0,"market_signal":0.0,"home_advantage":0.25}' 1.91
```

<!-- ADVANCED_PIPELINE:END -->

<!-- FREE_STATIC_HOSTING:START -->
## Free Hosting (GitHub Pages)

This repository includes a fully static GUI app at `docs/index.html`, deployable for free.

- Live URL pattern after push: `https://igor-kan.github.io/tennis-prediction-betting-system/`
- Workflow file: `.github/workflows/deploy-pages.yml`
- No paid backend required (client-side prediction + browser-stored bankroll)

<!-- FREE_STATIC_HOSTING:END -->
