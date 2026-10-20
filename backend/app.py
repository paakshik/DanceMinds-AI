"""FastAPI service exposing the DanceMinds dance-style ML model."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(BASE_DIR))

from config import API_PREFIX, DEFAULT_CORS_ORIGINS
from fastapi.middleware.cors import CORSMiddleware
from schemas import GenerateChoreographyRequest
from services.choreography import build_choreography_payload
from services.video_render import render_slideshow
from services.human_video import build_prompt, poll_replicate, submit_replicate
from dance_styles import DANCE_STYLES, ALL_STYLES
from schemas import HealthResponse, PredictFeaturesRequest, PredictSongRequest
from services.predictor import predictor
from services.audio_features import extract_features
from services.choreography import build_choreography_payload
from schemas import GenerateChoreographyRequest

app = FastAPI(
    title="DanceMinds AI - Dance Style Classifier",
    description="Predicts a dance form from a song title or audio features using a scikit-learn model.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=DEFAULT_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health():
    meta = predictor.metadata or {}
    return HealthResponse(
        status="ok",
        model_loaded=predictor.is_ready(),
        model_type=meta.get("model_type"),
        classes=len(meta.get("classes", [])),
        samples=meta.get("samples", 0),
    )


@app.get(f"{API_PREFIX}/styles")
def list_styles():
    return {"data": DANCE_STYLES, "total": len(ALL_STYLES)}


@app.get(f"{API_PREFIX}/metadata")
def metadata():
    if not predictor.metadata:
        raise HTTPException(status_code=503, detail="Model metadata unavailable.")
    return predictor.metadata


@app.post(f"{API_PREFIX}/predict")
def predict_song(req: PredictSongRequest):
    try:
        return predictor.predict_song(req.title, req.artist, req.genre, req.top_k)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@app.post(f"{API_PREFIX}/predict-features")
def predict_features(req: PredictFeaturesRequest):
    try:
        return predictor.predict_features(req.features, req.top_k)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post(f"{API_PREFIX}/analyze-audio")
async def analyze_audio(file: UploadFile = File(...), top_k: int = Form(5)):
    if not predictor.is_ready():
        raise HTTPException(status_code=503, detail="Model is not trained yet.")
    suffix = Path(file.filename or "audio.wav").suffix or ".wav"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        content = await file.read()
        tmp.write(content)
        tmp.flush()
        tmp.close()
        features = extract_features(tmp.name)
        result = predictor.predict_features(features, top_k=top_k)
        return {
            "filename": file.filename,
            "features": features,
            "prediction": result["prediction"],
            "notes": ["Audio features were extracted locally (ffmpeg + numpy/scipy)."],
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not analyze audio: {exc}")
    finally:
        Path(tmp.name).unlink(missing_ok=True)


@app.post(f"{API_PREFIX}/generate")
def generate_choreography(req: GenerateChoreographyRequest):
    try:
        payload = build_choreography_payload(
            dance_style=req.dance_style,
            age=req.age,
            height=req.height or "not specified",
            profession=req.profession or "General",
            video_quality=req.video_quality,
            features=req.features,
            song_title=req.song_title,
        )
        return {"data": payload}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post(f"{API_PREFIX}/generate-audio")
async def generate_from_audio(
    file: UploadFile = File(...),
    dance_style: str = Form(...),
    age: int = Form(18),
    height: str = Form("not specified"),
    profession: str = Form("General"),
    video_quality: str = Form("720p"),
    top_k: int = Form(5),
):
    suffix = Path(file.filename or "audio.wav").suffix or ".wav"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        content = await file.read()
        tmp.write(content)
        tmp.flush()
        tmp.close()
        features = extract_features(tmp.name)
        features["title"] = file.filename
        payload = build_choreography_payload(
            dance_style=dance_style,
            age=age,
            height=height,
            profession=profession,
            video_quality=video_quality,
            features=features,
            song_title=file.filename,
        )
        return {"features": features, "data": payload}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not generate choreography: {exc}")
    finally:
        Path(tmp.name).unlink(missing_ok=True)


@app.post(f"{API_PREFIX}/render-video")
def render_video(req: GenerateChoreographyRequest, background_tasks: BackgroundTasks):
    try:
        payload = build_choreography_payload(
            dance_style=req.dance_style,
            age=req.age,
            height=req.height or "not specified",
            profession=req.profession or "General",
            video_quality=req.video_quality,
            features=req.features,
            song_title=req.song_title,
        )
        out_path = render_slideshow(payload)
        background_tasks.add_task(lambda p=str(out_path): __import__("pathlib").Path(p).unlink(missing_ok=True))
        return FileResponse(str(out_path), media_type="video/mp4", filename="routine.mp4")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not render video: {exc}")


@app.post(f"{API_PREFIX}/render-video-audio")
async def render_video_from_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    dance_style: str = Form(...),
    age: int = Form(18),
    height: str = Form("not specified"),
    profession: str = Form("General"),
    video_quality: str = Form("720p"),
):
    suffix = Path(file.filename or "audio.wav").suffix or ".wav"
    audio_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        content = await file.read()
        audio_tmp.write(content)
        audio_tmp.flush()
        audio_tmp.close()
        features = extract_features(audio_tmp.name)
        features["title"] = file.filename
        payload = build_choreography_payload(
            dance_style=dance_style,
            age=age,
            height=height,
            profession=profession,
            video_quality=video_quality,
            features=features,
            song_title=file.filename,
        )
        out_path = render_slideshow(payload, audio_path=audio_tmp.name)
        background_tasks.add_task(lambda p=str(audio_tmp.name): Path(p).unlink(missing_ok=True))
        background_tasks.add_task(lambda p=str(out_path): Path(p).unlink(missing_ok=True))
        return FileResponse(str(out_path), media_type="video/mp4", filename="routine_with_audio.mp4")
    except Exception as exc:
        Path(audio_tmp.name).unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Could not render video: {exc}")


@app.post(f"{API_PREFIX}/render-human-video")
def render_human_video(req: GenerateChoreographyRequest):
    provider = os.getenv("VIDEO_API_PROVIDER", "replicate").lower()
    token = os.getenv("REPLICATE_API_TOKEN") or os.getenv("HF_TOKEN")
    if not token:
        raise HTTPException(
            status_code=400,
            detail=(
                "No video API token found. Set REPLICATE_API_TOKEN (or HF_TOKEN) in the environment. "
                "See backend/README.md for optional external video generation."
            ),
        )

    payload = build_choreography_payload(
        dance_style=req.dance_style,
        age=req.age,
        height=req.height or "not specified",
        profession=req.profession or "General",
        video_quality=req.video_quality,
        features=req.features,
        song_title=req.song_title,
    )
    prompt = build_prompt(payload)

    if provider == "replicate":
        model = os.getenv("VIDEO_MODEL", "minimax/video-01")
        try:
            prediction = submit_replicate(prompt, model, token, wait=True)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Video generation failed: {exc}")
        output = prediction.get("output")
        if isinstance(output, list):
            output = output[0] if output else None
        status = prediction.get("status", "unknown")
        if output and status in {"succeeded", "completed"}:
            return {
                "status": "succeeded",
                "provider": provider,
                "model": model,
                "prompt": prompt,
                "video_url": output,
                "prediction_id": prediction.get("id"),
            }
        return {
            "status": status,
            "provider": provider,
            "model": model,
            "prompt": prompt,
            "prediction_id": prediction.get("id"),
            "poll_url": f"{API_PREFIX}/render-human-video/{prediction.get('id')}",
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported VIDEO_API_PROVIDER: {provider}")


@app.get(f"{API_PREFIX}/render-human-video/{{prediction_id}}")
def render_human_video_status(prediction_id: str):
    token = os.getenv("REPLICATE_API_TOKEN")
    if not token:
        raise HTTPException(status_code=400, detail="REPLICATE_API_TOKEN is required to poll jobs.")
    try:
        prediction = poll_replicate(prediction_id, token)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not poll job: {exc}")
    output = prediction.get("output")
    if isinstance(output, list):
        output = output[0] if output else None
    return {
        "status": prediction.get("status"),
        "prediction_id": prediction.get("id"),
        "video_url": output,
        "error": prediction.get("error"),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
