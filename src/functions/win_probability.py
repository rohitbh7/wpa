from functools import lru_cache
from pathlib import Path

import pandas as pd
import xgboost as xgb

from functions.scoring import next_point

MODEL_PATH = Path(__file__).resolve().parents[2] / 'models' / 'xgb_model.json'


@lru_cache(maxsize=None)
def _load_booster(model_path):
    booster = xgb.Booster()
    booster.load_model(model_path)
    return booster


def _p1_win_prob(row_df, booster):
    X = row_df[booster.feature_names].astype(float)
    return float(booster.predict(xgb.DMatrix(X))[0])


def _score_str(row):
    sets = f"{row['P1SetsWon']}-{row['P2SetsWon']}"
    games = f"{row['P1GamesWon']}-{row['P2GamesWon']}"
    points = f"{row['P1Score']}-{row['P2Score']}"
    return f"{sets}; {games}; {points}"


def win_probabilities(row_df, model_path=MODEL_PATH):
    """Current and next-point win probabilities for a one-row match state.

    Returns a 3-row DataFrame (current, p1_wins_point, p2_wins_point) with
    the resulting score and each player's match win probability.
    """
    if len(row_df) != 1:
        raise ValueError(f"row_df must have exactly one row, got {len(row_df)}")

    booster = _load_booster(str(model_path))

    states = {
        'current': row_df,
        'p1_wins_point': next_point(row_df, 1),
        'p2_wins_point': next_point(row_df, 2),
    }

    records = []
    for scenario, state in states.items():
        p1_prob = _p1_win_prob(state, booster)
        records.append({
            'scenario': scenario,
            'score': _score_str(state.iloc[0]),
            'p1_win_prob': p1_prob,
            'p2_win_prob': 1 - p1_prob,
        })

    return pd.DataFrame.from_records(records)
