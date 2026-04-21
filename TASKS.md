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
