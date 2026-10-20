"""Generate a feature-labelled song corpus for dance-style classification."""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from config import RANDOM_STATE, SAMPLES_PER_STYLE, CORPUS_PATH
from dance_styles import ALL_STYLES, CATEGORY_PROFILE, STYLE_NUDGE, STYLE_BY_NAME, DANCE_STYLES

GENRE_BY_CATEGORY = {
    "Indian Classical": ["Classical", "Folk"],
    "Western": ["Pop", "Electronic", "Jazz", "Rock"],
    "Latin": ["Pop", "Latin", "Electronic"],
    "Ballroom": ["Jazz", "Classical", "Pop"],
    "Folk & Traditional": ["Folk", "Classical"],
    "Modern & Street": ["Hip-Hop", "Electronic", "Pop", "K-Pop"],
    "Cultural": ["Pop", "Folk", "Classical", "R&B"],
}

rng = np.random.default_rng(RANDOM_STATE)
random.seed(RANDOM_STATE)


def _clip(value, low, high):
    return float(min(max(value, low), high))


def generate_row(style: str, index: int) -> dict:
    category = STYLE_BY_NAME[style]
    profile = CATEGORY_PROFILE[category]
    nudge = STYLE_NUDGE.get(style, {})
    style_rng = np.random.default_rng(abs(hash(style)) % (2 ** 32))
    row = {"dance_style": style, "category": category}

    # per-style stable musical persona, so the classifier learns something
    # more specific than the broad category baseline.
    tempo_center = profile["tempo"][0] + style_rng.uniform(-18.0, 18.0)
    energy_center = _clip(profile["energy"][0] + style_rng.uniform(-0.12, 0.12), 0.2, 0.95)
    valence_center = _clip(profile["valence"][0] + style_rng.uniform(-0.10, 0.10), 0.1, 0.95)
    dance_center = _clip(profile["danceability"][0] + style_rng.uniform(-0.10, 0.10), 0.2, 0.98)
    acoustic_center = _clip(profile["acousticness"][0] + style_rng.uniform(-0.10, 0.10), 0.02, 0.95)

    # tempo
    c, s = profile["tempo"]
    nc, ns = nudge.get("tempo", (0.0, 1.0))
    tempo = rng.normal(tempo_center + nc, max(s * ns, 3.0))
    row["tempo"] = _clip(tempo, 40, 250)

    persona = {
        "energy": (energy_center, 0.06),
        "valence": (valence_center, 0.07),
        "danceability": (dance_center, 0.06),
        "acousticness": (acoustic_center, 0.07),
        "speechiness": profile["speechiness"],
        "instrumentalness": profile["instrumentalness"],
        "liveness": (0.18, 0.06),
    }

    # energy, valence, danceability, etc.
    for feature, (lo, hi) in {
        "energy": (0.0, 1.0),
        "valence": (0.0, 1.0),
        "danceability": (0.0, 1.0),
        "acousticness": (0.0, 1.0),
        "speechiness": (0.0, 1.0),
        "instrumentalness": (0.0, 1.0),
        "liveness": (0.0, 1.0),
    }.items():
        c, s = persona.get(feature, profile.get(feature, (0.2, 0.1)))
        if isinstance(c, tuple):
            c, s = c
        nc, ns = nudge.get(feature, (0.0, 1.0))
        val = rng.normal(c + nc, max(s * ns, 0.02))
        row[feature] = _clip(val, lo, hi)

    # loudness
    c, s = profile["loudness"]
    nc, ns = nudge.get("loudness", (0.0, 1.0))
    row["loudness"] = _clip(rng.normal(c + nc, s * ns), -22, 0)

    # musical metadata
    row["mode"] = int(rng.choice([0, 1], p=[0.35, 0.65]))
    row["key"] = int(rng.integers(0, 12))
    row["time_signature"] = int(rng.choice([3, 4, 5, 6], p=[0.05, 0.80, 0.05, 0.10]))
    row["genre"] = random.choice(GENRE_BY_CATEGORY[category])
    row["track_name"] = f"{style.replace(' ', '')} Groove {index + 1:03d}"
    row["artist"] = "DanceMinds Studio"
    return row


def build_corpus(samples_per_style: int = SAMPLES_PER_STYLE, seed: int = RANDOM_STATE) -> pd.DataFrame:
    rows = []
    for style in ALL_STYLES:
        for i in range(samples_per_style):
            rows.append(generate_row(style, i))
    frame = pd.DataFrame(rows)
    # shuffle
    frame = frame.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return frame


def main() -> None:
    CORPUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    frame = build_corpus()
    frame.to_csv(CORPUS_PATH, index=False)
    print(f"Wrote {len(frame)} rows covering {frame['dance_style'].nunique()} styles to {CORPUS_PATH}")
    print(frame["dance_style"].value_counts().head())


if __name__ == "__main__":
    main()