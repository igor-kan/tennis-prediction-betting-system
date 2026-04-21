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

<!-- API_CLI_TUI:START -->
## API + CLI + TUI

This project supports three operator interfaces:
- REST API (FastAPI backend)
- CLI client (`scripts/cli_api.py`)
- Terminal UI (`scripts/tui_api.py`)

Start local API:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8100
```

CLI usage:
```bash
python3 scripts/cli_api.py --help
python3 scripts/cli_api.py health
python3 scripts/cli_api.py ingest-public --limit 20
python3 scripts/cli_api.py list-events
python3 scripts/cli_api.py predict --event-id <event_id>
```

TUI usage:
```bash
python3 scripts/tui_api.py
```
Use keys: `h i e p r b s k f q`.

OpenAPI docs when backend runs locally:
- `http://127.0.0.1:8100/docs`
<!-- API_CLI_TUI:END -->

<!-- REPO_ANALYSIS_OVERVIEW_START -->
## Repository Analysis Snapshot

Generated: 2026-04-21

- Primary stack: Python
- Key paths: `backend`, `api`, `docs`, `scripts`, `.github/workflows`, `README.md`, `requirements.txt`
- Files scanned (capped): 47
- Test signal: Test-named files detected
- CI workflows present: Yes

### Quick Commands

Setup:
- `python3 -m pip install -r requirements.txt`

Run:
- `Review repository README for run/start command`

Quality:
- `Review CI/workflow commands in .github/workflows`

### Companion Docs

- `AGENTS.md`
- `TASKS.md`
- `PLANNING.md`
- `RESEARCH.md`
- `PROJECT_BRIEF.md`
<!-- REPO_ANALYSIS_OVERVIEW_END -->

<!-- CORS_AND_GUI_BRIDGE:START -->
## GUI <-> API Bridge + CORS

The static GUI (`docs/index.html`) now includes an **API Bridge** card.

- Set API base URL (example: `http://127.0.0.1:8100`)
- Use bridge buttons to call live API endpoints from GUI
- Keep using local browser mode when API is not set

CORS is enabled in backend API via `CORS_ALLOWED_ORIGINS`:
```bash
# allow any origin (default)
export CORS_ALLOWED_ORIGINS="*"

# or restrict to specific origins
export CORS_ALLOWED_ORIGINS="https://igor-kan.github.io,http://127.0.0.1:5500"
```
<!-- CORS_AND_GUI_BRIDGE:END -->
