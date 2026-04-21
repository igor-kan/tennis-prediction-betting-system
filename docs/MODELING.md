# Modeling Notes

Current baseline model is a deterministic logistic-style scorer on engineered public-data features.

## Baseline Features
- rating_delta (Elo/Power rating difference)
- form_delta (recent performance differential)
- rest_delta (rest/travel differential)
- injury_delta (availability differential)
- market_signal (optional market odds signal)

## Roadmap
- Replace baseline with sport-specific gradient boosting / Bayesian models.
- Calibrate probabilities (Platt/Isotonic) per market type.
- Add uncertainty estimates and confidence intervals.
