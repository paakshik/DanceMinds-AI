from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PredictSongRequest(BaseModel):
    title: str = Field(..., min_length=1)
    artist: Optional[str] = None
    genre: Optional[str] = None
    top_k: int = Field(5, ge=1, le=10)


class PredictFeaturesRequest(BaseModel):
    features: Dict[str, Any]
    top_k: int = Field(5, ge=1, le=10)


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_type: Optional[str] = None
    classes: int = 0
    samples: int = 0


class GenerateChoreographyRequest(BaseModel):
    dance_style: str = Field(..., min_length=1)
    age: int = Field(18, ge=3, le=100)
    height: Optional[str] = None
    profession: Optional[str] = None
    video_quality: str = Field("720p")
    features: Optional[Dict[str, Any]] = None
    song_title: Optional[str] = None