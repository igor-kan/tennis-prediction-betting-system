# AGENTS

Last updated: 2026-04-21

## Ownership
- Product owner: model/product scope, legal compliance, deployment approvals.
- Engineering agent: ingestion, modeling, betting execution logic, observability.

## Engineering Policy
- Never place live bets without explicit operator action.
- Keep paper mode as default provider.
- Log prediction confidence, edge, and final decision reason.
- Keep all model inputs reproducible from public data sources.

<!-- REPO_DOCS_REFRESH_START -->
# AGENTS

Repository-specific working guide for coding agents on **Tennis Prediction and Betting System**.

## Snapshot
- Repository: `tennis-prediction-betting-system`
- Path: `/home/igorkan/repos/tennis-prediction-betting-system`
- Purpose: Production-oriented repository for Tennis outcome prediction and betting execution using publicly available data.
- Detected stack: Unknown

## Commands
Setup:
- `Refer to README for setup`

Run:
- `Refer to README for run/start command`

Quality checks:
- `Add and run repository-specific tests`

## Collaboration Rules
- Scope changes to this repository only.
- Prefer incremental and verifiable edits.
- Update `PROJECT_BRIEF.md`, `TASKS.md`, `PLANNING.md`, and `RESEARCH.md` when behavior changes.
- Avoid destructive git operations unless explicitly requested.

## References
- See `PROJECT_BRIEF.md` for human/agent shared orientation.
<!-- REPO_DOCS_REFRESH_END -->

<!-- ZERO_BUDGET_HOSTING:START -->
## Zero-Budget Hosting Policy
- Primary deployment target is GitHub Pages only (public repo, free tier).
- Do not require paid hosting for the core user flow.
- Keep `docs/index.html` fully usable as the production demo path.
- Paid services are optional and must stay disabled by default.
<!-- ZERO_BUDGET_HOSTING:END -->

<!-- API_CLI_TUI_AGENT:START -->
## Interface Contract
- Preserve compatibility for REST API, CLI (`scripts/cli_api.py`), and TUI (`scripts/tui_api.py`).
- New betting features should be exposed through API first, then wired into CLI/TUI.
<!-- API_CLI_TUI_AGENT:END -->
