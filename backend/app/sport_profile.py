SPORT_NAME = "Tennis"
ESPN_SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/tennis/scoreboard"

# Baseline weights for public-data features.
FEATURE_WEIGHTS = {
    "rating_delta": 1.10,
    "form_delta": 0.85,
    "rest_delta": 0.40,
    "injury_delta": 0.70,
    "market_signal": 0.35,
    "home_advantage": 0.30,
}

MODEL_CONFIDENCE_FLOOR = 0.55
