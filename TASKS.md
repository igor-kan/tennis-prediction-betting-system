# TASKS

Last updated: 2026-04-21

## Completed in v3
- [x] Added persistent DB models for events, bets, and bankroll.
- [x] Added migration runner and initial SQL migration.
- [x] Added public ESPN ETL ingest endpoint.
- [x] Added interactive web UI for betting workflow.
- [x] Added stake recommendation and bet settlement lifecycle.

## Next Milestones
- [ ] Add sport-specific feature enrichment pipeline.
- [ ] Add async job scheduler for periodic ETL refresh.
- [ ] Add auth and role-based controls for live betting.
- [ ] Add richer performance analytics (CLV, drawdown, sharpe-like metrics).
- [ ] Add multi-book odds normalization for better edge estimates.

<!-- ADVANCED_TASKS:START -->
## Advanced Modeling/Data Work
- [x] Added multi-model ensemble prediction engine.
- [x] Added Monte Carlo uncertainty and EV analysis support.
- [x] Added calibration training script.
- [x] Added feature dataset builder from public raw feeds.
- [x] Added advanced backtest script (brier/logloss/ROI/drawdown).
- [ ] Add sport-specific feature enrichers (injury/news/schedule intensity).
- [ ] Add model registry and rolling retrain schedule.

<!-- ADVANCED_TASKS:END -->

<!-- ZERO_BUDGET_TASKS:START -->
## Zero-Budget Deployment Tasks
- [x] Static web GUI implemented in `docs/index.html`.
- [x] GitHub Pages workflow added in `.github/workflows/deploy-pages.yml`.
- [x] Core demo flow runs without paid infrastructure.
- [ ] Verify GitHub Pages deploy health monthly.
<!-- ZERO_BUDGET_TASKS:END -->

<!-- API_CLI_TUI_TASKS:START -->
## API + CLI + TUI Tasks
- [x] FastAPI endpoints available for prediction/betting workflows.
- [x] Added API CLI client in `scripts/cli_api.py`.
- [x] Added terminal TUI client in `scripts/tui_api.py`.
- [ ] Add integration tests for CLI/TUI command paths.
<!-- API_CLI_TUI_TASKS:END -->

<!-- REPO_DOCS_REFRESH_START -->
# TASKS

Updated: 2026-04-21
Repository: `tennis-prediction-betting-system`

## Immediate
- [ ] Run and verify setup command(s): `python3 -m pip install -r requirements.txt`
- [ ] Run and verify primary start command(s): `Review repository README for run/start command`
- [ ] Run quality checks: `Review CI/workflow commands in .github/workflows`
- [ ] Confirm key paths are still accurate: `backend`, `api`, `docs`, `scripts`, `.github/workflows`, `README.md`, `requirements.txt`

## Next
- [ ] Prioritize top 3 reliability improvements for this repository.
- [ ] Expand automated tests around highest-risk areas.
- [ ] Tighten command documentation in README for onboarding speed.

## Ongoing Maintenance
- [ ] Keep README and architecture notes synchronized with code changes.
- [ ] Track technical debt and refactor candidates in `PLANNING.md`.
- [ ] Track unknowns and external dependencies in `RESEARCH.md`.

## Completed Recently
- [x] Repository-specific task file refreshed on 2026-04-21.
<!-- REPO_DOCS_REFRESH_END -->

<!-- CORS_GUI_TASKS:START -->
## API/GUI Bridge Hardening
- [x] Added API bridge controls to static GUI.
- [x] Enabled API CORS for browser-based API usage.
- [x] Hardened CLI/TUI with better command/error handling.
- [ ] Add end-to-end browser automation for GUI bridge.
<!-- CORS_GUI_TASKS:END -->
