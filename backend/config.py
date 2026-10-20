"""Shared configuration for the DanceMinds ML backend."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "dance_classifier.joblib"
METADATA_PATH = MODELS_DIR / "metadata.json"
CORPUS_PATH = DATA_DIR / "song_corpus.csv"

# API
API_PREFIX = "/api"
DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "null",
]

# Training
RANDOM_STATE = 42
SAMPLES_PER_STYLE = 45
TEST_SIZE = 0.2
