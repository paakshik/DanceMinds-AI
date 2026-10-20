"""Smoke tests for the dance-style predictor."""

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from services.predictor import DanceStylePredictor


def test_model_loads():
    p = DanceStylePredictor()
    assert p.is_ready()
    assert len(p.metadata["classes"]) == 53


def test_predict_features_returns_probability():
    p = DanceStylePredictor()
    res = p.predict_features({
        "tempo": 140, "energy": 0.8, "valence": 0.7, "danceability": 0.85,
        "acousticness": 0.1, "speechiness": 0.05, "instrumentalness": 0.1,
        "liveness": 0.2, "loudness": -6, "mode": 1, "key": 4,
        "time_signature": 4, "genre": "Pop",
    })
    pred = res["prediction"]
    assert pred["dance_style"] in p.metadata["classes"]
    assert 0.0 <= pred["confidence"] <= 1.0
    assert len(pred["top_k"]) == 5


def test_predict_song_never_crashes():
    p = DanceStylePredictor()
    res = p.predict_song("Unknown Title", "Unknown Artist", "rock")
    assert "prediction" in res
    assert res["prediction"]["dance_style"] in p.metadata["classes"]