"""Train and persist the DanceMinds dance-style classifier."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, top_k_accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from config import MODEL_PATH, METADATA_PATH, TEST_SIZE, RANDOM_STATE
from config import CORPUS_PATH
from dance_styles import ALL_STYLES
from training.build_dataset import build_corpus

NUMERIC_FEATURES = [
    "tempo", "energy", "valence", "danceability", "acousticness",
    "speechiness", "instrumentalness", "liveness", "loudness",
    "mode", "key", "time_signature",
]
CATEGORICAL_FEATURES = ["genre"]

TARGET = "dance_style"


def build_preprocess():
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
    ])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer(
        transformers=[
            ("num", numeric, NUMERIC_FEATURES),
            ("cat", categorical, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def make_pipeline(model):
    return Pipeline([("preprocess", build_preprocess()), ("model", model)])


def main() -> None:
    if CORPUS_PATH.exists():
        df = pd.read_csv(CORPUS_PATH)
        print(f"Loaded corpus: {len(df)} rows from {CORPUS_PATH}")
    else:
        print("Corpus not found; generating...")
        df = build_corpus()
        df.to_csv(CORPUS_PATH, index=False)

    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET].astype(str)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )

    candidates = {
        "random_forest": RandomForestClassifier(
            n_estimators=350, min_samples_leaf=2, n_jobs=-1, random_state=RANDOM_STATE
        ),
        "hist_gradient_boosting": HistGradientBoostingClassifier(
            max_iter=300, learning_rate=0.08, random_state=RANDOM_STATE
        ),
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    results = {}
    for name, estimator in candidates.items():
        pipe = make_pipeline(estimator)
        scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="accuracy", n_jobs=-1)
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        test_acc = accuracy_score(y_test, pred)
        # top-3 accuracy
        proba = pipe.predict_proba(X_test)
        top3 = top_k_accuracy_score(y_test, proba, k=min(3, len(pipe.classes_)), labels=pipe.classes_)
        results[name] = {"cv_mean": float(scores.mean()), "cv_std": float(scores.std()), "test_accuracy": float(test_acc), "test_top3_accuracy": float(top3), "pipeline": pipe}
        print(f"{name}: cv={scores.mean():.4f}+/-{scores.std():.4f} test={test_acc:.4f} top3={top3:.4f}")

    best_name = max(results, key=lambda n: results[n]["test_accuracy"])
    best = results[best_name]["pipeline"]
    print(f"Best model: {best_name}")

    # Refit on the full dataset for deployment.
    best.fit(X, y)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best, MODEL_PATH)

    metadata = {
        "version": "1.0.0",
        "model_type": best_name,
        "classes": list(best.classes_),
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "all_features": NUMERIC_FEATURES + CATEGORICAL_FEATURES,
        "samples": int(len(df)),
        "samples_per_style": int(df["dance_style"].value_counts().iloc[0]),
        "metrics": {
            n: {
                "cv_mean": r["cv_mean"],
                "cv_std": r["cv_std"],
                "test_accuracy": r["test_accuracy"],
                "test_top3_accuracy": r["test_top3_accuracy"],
            } for n, r in results.items()
        },
        "best": best_name,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "random_state": RANDOM_STATE,
        "note": "Trained on a seeded feature corpus derived from musical priors. Replace training/data with measured audio features for production-grade accuracy.",
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Saved model to {MODEL_PATH}")
    print(f"Saved metadata to {METADATA_PATH}")


if __name__ == "__main__":
    main()
