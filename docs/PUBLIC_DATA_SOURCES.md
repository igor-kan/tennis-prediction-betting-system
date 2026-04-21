# Public Data Sources (Tennis)

Use publicly available APIs/datasets to build features and labels.

## Suggested Sources
- ATP/WTA public results datasets\n- Player form/head-to-head histories\n- Public odds archives

## Data Contract
Minimum required fields per event:
- event_id
- start_time_iso
- home_team / away_team (or player_a / player_b)
- market_odds (decimal)
- engineered feature set (elo delta, form, injuries/news proxies, rest/travel proxies)

## Quality Rules
- Keep source timestamp and URL/reference for every record.
- Deduplicate events by provider_event_id + start_time.
- Reject stale records beyond configurable cutoff.
