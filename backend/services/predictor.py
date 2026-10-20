"""Inference helpers for the DanceMinds dance-style classifier."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from difflib import SequenceMatcher

BASE_DIR = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(BASE_DIR))

from config import MODEL_PATH, METADATA_PATH, CORPUS_PATH
from dance_styles import STYLE_BY_NAME, ALL_STYLES, CATEGORY_PROFILE
from dance_styles import DANCE_STYLES


class DanceStylePredictor:
    def __init__(self):
        self.model = None
        self.metadata = None
        self.corpus: Optional[pd.DataFrame] = None
        self._load()

    def _load(self):
        if MODEL_PATH.exists():
            self.model = joblib.load(MODEL_PATH)
        if METADATA_PATH.exists():
            self.metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        if CORPUS_PATH.exists():
            self.corpus = pd.read_csv(CORPUS_PATH)

    @property
    def numeric_features(self) -> List[str]:
        return self.metadata["numeric_features"] if self.metadata else []

    @property
    def categorical_features(self) -> List[str]:
        return self.metadata["categorical_features"] if self.metadata else []

    def is_ready(self) -> bool:
        return self.model is not None

    # ------------------------------------------------------------------ #
    def _normalise_features(self, features: Dict[str, Any]) -> pd.DataFrame:
        row = {}
        defaults = {
            "tempo": 120.0, "energy": 0.6, "valence": 0.5, "danceability": 0.6,
            "acousticness": 0.3, "speechiness": 0.05, "instrumentalness": 0.2,
            "liveness": 0.15, "loudness": -9.0, "mode": 1, "key": 0,
            "time_signature": 4, "genre": "Pop",
        }
        for name in self.numeric_features + self.categorical_features:
            value = features.get(name, defaults.get(name))
            row[name] = value
        frame = pd.DataFrame([row])
        # coerce numerics
        for col in self.numeric_features:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
        return frame

    def predict_features(self, features: Dict[str, Any], top_k: int = 5) -> Dict[str, Any]:
        if not self.is_ready():
            raise RuntimeError("Model is not trained yet. Run training/train.py first.")
        frame = self._normalise_features(features)
        proba = self.model.predict_proba(frame)[0]
        classes = list(self.model.classes_)
        order = np.argsort(proba)[::-1]
        top = []
        for idx in order[:top_k]:
            style = classes[idx]
            top.append({
                "dance_style": style,
                "category": STYLE_BY_NAME.get(style, "Unknown"),
                "probability": float(proba[idx]),
            })
        best = top[0]
        return {
            "prediction": {
                "dance_style": best["dance_style"],
                "category": best["category"],
                "confidence": best["probability"],
                "top_k": top,
            },
            "features_used": {k: (None if (isinstance(v, float) and math.isnan(v)) else v) for k, v in frame.iloc[0].to_dict().items()},
        }

    # ------------------------------------------------------------------ #
    def _fuzzy_find_song(self, title: str, artist: Optional[str] = None) -> Optional[pd.Series]:
        if self.corpus is None or self.corpus.empty or not title:
            return None
        if not title:
            return None
        query = title.strip().lower()
        best_idx = None
        best_score = 0.0
        names = self.corpus["track_name"].astype(str).tolist()
        for i, name in enumerate(names):
            score = SequenceMatcher(None, query, name.lower()).ratio() * 100
            if score > best_score:
                best_score = score
                best_idx = i
        if best_score < 72:
            # try title + artist combined
            combined = (self.corpus["track_name"].astype(str) + " " + self.corpus["artist"].astype(str)).str.lower().tolist()
            q2 = f"{title} {artist or ''}".strip().lower()
            for i, name in enumerate(combined):
                score = SequenceMatcher(None, q2, name).ratio() * 100
                if score > best_score:
                    best_score = score
                    best_idx = i
            if best_score < 72:
                return None
        return self.corpus.iloc[best_idx] if best_idx is not None else None

    GENRE_TO_CATEGORY = {
        "hip-hop": "Modern & Street", "hip hop": "Modern & Street",
        "pop": "Western", "electronic": "Modern & Street", "edm": "Modern & Street",
        "jazz": "Western", "classical": "Indian Classical", "folk": "Folk & Traditional",
        "latin": "Latin", "salsa": "Latin", "tango": "Latin", "ballroom": "Ballroom",
        "bollywood": "Cultural", "indian": "Indian Classical", "afro": "Modern & Street",
        "rock": "Western", "r&b": "Modern & Street", "k-pop": "Modern & Street", "kpop": "Modern & Street",
    }

    def _profile_for_category(self, category: str) -> Dict[str, Any]:
        profile = CATEGORY_PROFILE.get(category, CATEGORY_PROFILE["Western"])
        row = {}
        for feat in ["tempo", "energy", "valence", "danceability", "acousticness",
                     "speechiness", "instrumentalness", "liveness"]:
            vals = profile.get(feat, (0.3, 0.1))
            if isinstance(vals, tuple):
                c = vals[0]
            else:
                c = vals
            row[feat] = float(c)
        lc, _ = profile["loudness"]
        row["loudness"] = float(lc)
        row["mode"] = 1
        row["key"] = 0
        row["time_signature"] = 4
        row["genre"] = "Pop"
        return row

    def _features_from_song(self, title: str, artist: Optional[str], genre: Optional[str]) -> (Dict[str, Any], Optional[pd.Series], List[str]):
        notes: List[str] = []
        matched = self._fuzzy_find_song(title, artist)
        if matched is not None:
            features = {col: matched[col] for col in self.numeric_features + self.categorical_features if col in matched.index}
            notes.append(f"Matched a similar entry in the training corpus (score >= 72).")
            return features, matched, notes

        notes.append("No close match in the corpus; falling back to feature priors.")
        # keyword -> style
        lowered = f"{title} {artist or ''} {genre or ''}".lower()
        for style in ALL_STYLES:
            if style.lower().replace(" ", "") in lowered.replace(" ", "") or style.lower() in lowered:
                cat = STYLE_BY_NAME[style]
                feats = self._profile_for_category(cat)
                # nudge towards this style being the strongest prior
                feats["_hint_style"] = style
                notes.append(f"Keyword match suggested '{style}'.")
                return feats, None, notes

        category = None
        if genre:
            category = self.GENRE_TO_CATEGORY.get(genre.strip().lower())
        if category is None:
            # try to infer from title words
            for key, cat in self.GENRE_TO_CATEGORY.items():
                if key in lowered:
                    category = cat
                    break
        if category is None:
            category = "Western"
            notes.append("Genre could not be inferred; using 'Western' baseline.")

        feats = self._profile_for_category(category)
        notes.append(f"Baseline feature profile for category '{category}' was used.")
        return feats, None, notes

    def predict_song(self, title: str, artist: Optional[str] = None, genre: Optional[str] = None, top_k: int = 5) -> Dict[str, Any]:
        if not self.is_ready():
            raise RuntimeError("Model is not trained yet. Run training/train.py first.")
        features, matched, notes = self._features_from_song(title, artist, genre)
        hint_style = features.pop("_hint_style", None)
        result = self.predict_features(features, top_k=top_k)

        # If we had a strong keyword hint, ensure it is surfaced.
        if hint_style is not None and result["prediction"]["dance_style"] != hint_style:
            # boost hint probabilistically not possible; attach as a note
            notes.append(f"Keyword hint '{hint_style}' is not the model's top choice; showing model ranking.")

        response: Dict[str, Any] = {
            "input": {"title": title, "artist": artist, "genre": genre},
            "matched_song": None if matched is None else {
                "track_name": str(matched.get("track_name")),
                "artist": str(matched.get("artist")),
                "dance_style": str(matched.get("dance_style")),
                "category": str(matched.get("category")),
            },
            "features_used": result["features_used"],
            "prediction": result["prediction"],
            "notes": notes,
        }
        return response


predictor = DanceStylePredictor()
