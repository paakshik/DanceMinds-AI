"""Optional adapter for external human dance video generation APIs."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict


def build_prompt(payload: Dict[str, Any]) -> str:
    req = payload.get("request", {})
    music = payload.get("music", {})
    style = req.get("danceStyle", "dance")
    bpm = music.get("bpm", "")
    genre = music.get("genre", "")
    title = music.get("title", "")
    return (
        f"A realistic human dancer performing {style} dance, full body view, "
        f"dance studio lighting, clean background, smooth choreography, "
        f"professional dance tutorial, {bpm} BPM {genre} music, "
        f"high quality, 1080p. Song context: {title}."
    )


def submit_replicate(prompt: str, model: str, token: str, wait: bool = True) -> Dict[str, Any]:
    url = f"https://api.replicate.com/v1/models/{model}/predictions"
    data = json.dumps({"input": {"prompt": prompt}}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    if wait:
        req.add_header("Prefer", "wait")
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Replicate error {exc.code}: {body}")


def poll_replicate(prediction_id: str, token: str) -> Dict[str, Any]:
    url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))
