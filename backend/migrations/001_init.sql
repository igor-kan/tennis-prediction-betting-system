CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    participants_json TEXT NOT NULL,
    start_time_iso TEXT NOT NULL,
    market_odds_decimal REAL NOT NULL,
    features_json TEXT NOT NULL,
    source TEXT NOT NULL,
    created_at_ms INTEGER NOT NULL,
    updated_at_ms INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS bets (
    ticket_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    selection TEXT NOT NULL,
    stake_amount REAL NOT NULL,
    odds_decimal REAL NOT NULL,
    provider TEXT NOT NULL,
    status TEXT NOT NULL,
    outcome TEXT,
    payout REAL NOT NULL DEFAULT 0,
    placed_at_ms INTEGER NOT NULL,
    settled_at_ms INTEGER
);

CREATE INDEX IF NOT EXISTS idx_bets_event_id ON bets(event_id);

CREATE TABLE IF NOT EXISTS bankroll (
    id INTEGER PRIMARY KEY,
    currency TEXT NOT NULL,
    starting_balance REAL NOT NULL,
    balance REAL NOT NULL
);

INSERT OR IGNORE INTO bankroll (id, currency, starting_balance, balance)
VALUES (1, 'USD', 10000.0, 10000.0);
