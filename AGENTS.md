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

This file contains repository-specific working guidance for coding agents collaborating on **tennis-prediction-betting-system**.

## Project Snapshot
- Repository: `tennis-prediction-betting-system`
- Path: `/home/igorkan/repos/tennis-prediction-betting-system`
- Purpose: Repository for Tennis outcome prediction and betting workflows using publicly available data.
- Primary Stack: Python

## Local Commands
Setup:
- `python3 -m pip install -r requirements.txt`

Run:
- `Review repository README for run/start command`

Quality Checks:
- `Review CI/workflow commands in .github/workflows`

## Agent Workflow
- Make changes that stay scoped to this repository.
- Prefer small, verifiable increments over large speculative rewrites.
- Update docs and task files in this repository when behavior or interfaces change.
- Avoid destructive git operations unless explicitly requested.

## Definition Of Done
- Relevant commands/tests complete successfully for this repository.
- Documentation reflects implemented behavior.
- Remaining risks and follow-ups are captured in `TASKS.md` and `RESEARCH.md`.
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
