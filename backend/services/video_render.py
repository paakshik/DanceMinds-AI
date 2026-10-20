"""Render a readable choreography slideshow video (ffmpeg + Pillow)."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path
from typing import Any, Dict, List

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1280, 720
SECONDS_PER_SLIDE = 6
BG = (15, 18, 32)
ACCENT = (139, 92, 246)
TEXT = (240, 240, 245)
MUTED = (180, 185, 210)

FONT_CANDIDATES = [
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
]


def _font(size: int):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _wrap(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if draw.textlength(test, font=font) <= max_width or not current:
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _render_slide(title: str, lines: List[str], accent: str = "") -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    # accent bar
    draw.rectangle((80, 90, 1040, 98), fill=ACCENT)
    title_font = _font(52)
    body_font = _font(34)
    small_font = _font(26)

    # Title
    y = 130
    for line in _wrap(draw, title, title_font, WIDTH - 160):
        draw.text((80, y), line, font=title_font, fill=TEXT)
        y += 62

    if accent:
        y += 10
        draw.text((80, y), accent, font=small_font, fill=MUTED)
        y += 40

    y += 20
    for line in lines:
        for wrapped in _wrap(draw, line, body_font, WIDTH - 160):
            draw.text((80, y), wrapped, font=body_font, fill=TEXT)
            y += 44
        y += 12
        if y > HEIGHT - 120:
            break

    # footer
    draw.text((80, HEIGHT - 60), "DanceMinds AI - choreography guide", font=small_font, fill=MUTED)
    return img


def render_slideshow(payload: Dict[str, Any], out_path: Path | None = None, audio_path: str | Path | None = None) -> Path:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg is required for video rendering.")

    music = payload.get("music", {})
    steps = payload.get("videoSteps", [])
    if not steps:
        raise ValueError("No videoSteps to render.")

    tmp_dir = Path(tempfile.mkdtemp(prefix="dm_slides_"))
    slide_paths: List[Path] = []

    # Intro slide
    intro_lines = [
        f"Style: {payload.get('request', {}).get('danceStyle', 'Dance')}",
        f"Song: {music.get('title', 'Unknown')}",
        f"BPM: {music.get('bpm', '?')}  Energy: {music.get('energy', '?')}/100",
        f"Age: {payload.get('request', {}).get('age', '?')}  Profession: {payload.get('request', {}).get('profession', 'General')}",
        "Follow each step at your own pace. Pause and repeat as needed.",
    ]
    intro = _render_slide("DanceMinds AI routine", intro_lines, "Prepared from your uploaded song")
    ip = tmp_dir / "slide_00_intro.png"
    intro.save(ip)
    slide_paths.append(ip)

    for i, step in enumerate(steps, start=1):
        lines = [
            f"Duration: {step.get('duration', '')}  |  Counts: {step.get('counts', '')}",
            f"Focus: {step.get('focus', '')}",
            step.get("description", ""),
            f"Music cue: {step.get('musicCue', '')}",
        ]
        if step.get("coachTip"):
            lines.append(f"Tip: {step.get('coachTip')}")
        slide = _render_slide(f"Step {i}: {step.get('title', '')}", lines)
        sp = tmp_dir / f"slide_{i:02d}.png"
        slide.save(sp)
        slide_paths.append(sp)

    # Summary slide
    summary = payload.get("summary", {})
    summary_lines = [
        f"Total steps: {summary.get('totalVideos', len(steps))}",
        f"Total duration: {summary.get('totalDurationLabel', '')}",
        *summary.get("insights", []),
    ]
    summary_slide = _render_slide("Routine complete", summary_lines, "Cool down and hydrate")
    ssp = tmp_dir / "slide_99_summary.png"
    summary_slide.save(ssp)
    slide_paths.append(ssp)

    if out_path is None:
        out_path = tmp_dir / "routine.mp4"

    # Build ffmpeg concat filter
    inputs = []
    filter_parts = []
    for idx, sp in enumerate(slide_paths):
        inputs += ["-loop", "1", "-t", str(SECONDS_PER_SLIDE), "-i", str(sp)]
        filter_parts.append(f"[{idx}:v]")
    concat = "".join(filter_parts) + f"concat=n={len(slide_paths)}:v=1:a=0[outv]"
    cmd = [ffmpeg, "-y", *inputs, "-filter_complex", concat, "-map", "[outv]", "-r", "30", "-pix_fmt", "yuv420p", "-c:v", "libx264", str(out_path)]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    if audio_path:
        final_path = out_path.with_name(out_path.stem + "_av" + out_path.suffix)
        mux_cmd = [
            ffmpeg, "-y",
            "-i", str(out_path),
            "-i", str(audio_path),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            str(final_path),
        ]
        subprocess.run(mux_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        out_path.unlink(missing_ok=True)
        return final_path

    return out_path
