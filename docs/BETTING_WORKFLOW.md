# Betting Workflow (v3)

1. Run public ETL ingestion to load latest events.
2. Review event list and run predictions.
3. Request stake recommendation and verify risk constraints.
4. Place bet (paper by default).
5. Settle event outcome and review ROI/performance.

## Persistence
- Events, bets, and bankroll are persisted in SQLite by default.
- Migration files are in `backend/migrations`.
- Run migrations manually with `scripts/migrate.sh`.
