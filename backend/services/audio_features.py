"""Extract musically-relevant features from an audio file without librosa."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
from scipy import signal

FFMPEG = shutil.which("ffmpeg")


def _convert_to_wav(src: Path) -> Path:
    if src.suffix.lower() == ".wav":
        return src
    if FFMPEG is None:
        raise RuntimeError("ffmpeg is required to decode non-WAV audio but was not found on PATH.")
    out = Path(tempfile.mktemp(suffix=".wav"))
    subprocess.run(
        [FFMPEG, "-y", "-i", str(src), "-ac", "1", "-ar", "22050", str(out)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
    )
    return out


def _read_wav(path: Path):
    with wave.open(str(path), "rb") as wf:
        sr = wf.getframerate()
        n = wf.getnframes()
        sw = wf.getsampwidth()
        channels = wf.getnchannels()
        raw = wf.readframes(n)
    if sw == 1:
        data = np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128
        data = data / 128.0
    elif sw == 2:
        data = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    elif sw == 3:
        # unpack 24-bit
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        vals = b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8) | (b[:, 2].astype(np.int32) << 16)
        vals = np.where(vals >= 0x800000, vals - 0x1000000, vals)
        data = vals.astype(np.float32) / 8388608.0
    elif sw == 4:
        data = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"Unsupported sample width: {sw}")
    if channels > 1:
        data = data.reshape(-1, channels).mean(axis=1)
    return data, sr


def _autocorrelation_tempo(envelope: np.ndarray, sr: int, hop: int) -> float:
    env = envelope - np.mean(envelope)
    if np.all(env == 0):
        return 120.0
    corr = np.correlate(env, env, mode="full")
    corr = corr[len(corr) // 2:]
    # lag range for 50..220 BPM
    min_lag = int(sr / hop * 60 / 220)
    max_lag = int(sr / hop * 60 / 50)
    max_lag = min(max_lag, len(corr) - 1)
    if max_lag <= min_lag:
        return 120.0
    segment = corr[min_lag:max_lag]
    if segment.size == 0:
        return 120.0
    peak = int(np.argmax(segment)) + min_lag
    if peak == 0:
        return 120.0
    bpm = 60.0 * sr / (hop * peak)
    return float(np.clip(bpm, 40, 240))


def extract_features(path: str | Path) -> dict:
    src = Path(path)
    wav_path = _convert_to_wav(src)
    cleanup = wav_path != src
    try:
        samples, sr = _read_wav(wav_path)
    finally:
        if cleanup and wav_path.exists():
            wav_path.unlink(missing_ok=True)

    if samples.size == 0:
        raise ValueError("Audio file is empty.")

    # mono float
    samples = samples.astype(np.float32)
    n = samples.size

    # frame-based features
    hop = max(1, sr // 20)  # 50ms
    frame_len = hop * 2
    n_frames = max(1, n // hop)
    frames = samples[: n_frames * hop].reshape(n_frames, hop)
    frame_rms = np.sqrt(np.mean(frames ** 2, axis=1) + 1e-12)

    # RMS energy normalised (compared to a 0dBFS reference)
    rms = float(np.sqrt(np.mean(samples ** 2) + 1e-12))
    energy = float(np.clip(rms * 4, 0.0, 1.0))

    # zero crossing rate
    zcr = float(np.mean(np.abs(np.diff(np.sign(samples)))) / 2.0)

    # spectral features via STFT
    f, t, Zxx = signal.stft(samples, fs=sr, nperseg=2048, noverlap=1024)
    mag = np.abs(Zxx) + 1e-12
    col_sum = mag.sum(axis=0) + 1e-12
    centroid = float(np.mean(np.sum(f[:, None] * mag, axis=0) / col_sum))
    bandwidth = float(np.mean(np.sqrt(np.sum(((f[:, None] - centroid) ** 2) * mag, axis=0) / col_sum)))
    rolloff = float(np.clip(np.mean(centroid * 1.7), 0, sr / 2))
    flatness = 0.5

    # Danceability proxy: regularity of the onset envelope
    onset_env = np.abs(np.diff(frame_rms))
    tempo = _autocorrelation_tempo(frame_rms, sr, hop)
    pulse_regularity = float(np.clip(1.0 - np.std(np.diff(frame_rms)) / (np.mean(frame_rms) + 1e-6), 0, 1))

    # Normalise spectral scalars to feature ranges used by the model
    centroid_norm = float(np.clip(centroid / 4000.0, 0, 1))
    rolloff_norm = float(np.clip(rolloff / 8000.0, 0, 1))
    flatness_norm = float(np.clip(flatness, 0, 1))

    # Heuristic valence: bright spectra + high tempo
    valence = float(np.clip(0.35 * centroid_norm + 0.25 * (tempo / 200.0) + 0.2 * energy + 0.2, 0, 1))
    danceability = float(np.clip(0.4 * pulse_regularity + 0.3 * energy + 0.2 * (tempo / 180.0) + 0.1, 0, 1))
    acousticness = float(np.clip(1.0 - (centroid_norm * 0.5 + rolloff_norm * 0.3 + energy * 0.2), 0, 1))
    speechiness = float(np.clip(zcr * 2.5, 0, 1))
    instrumentalness = float(np.clip(1.0 - speechiness - 0.1, 0, 1))
    liveness = float(np.clip(np.std(frame_rms) / (np.mean(frame_rms) + 1e-6) * 0.5, 0, 1))
    loudness = float(np.clip(20 * np.log10(rms + 1e-9), -40, 0))

    features = {
        "tempo": tempo,
        "energy": energy,
        "valence": valence,
        "danceability": danceability,
        "acousticness": acousticness,
        "speechiness": speechiness,
        "instrumentalness": instrumentalness,
        "liveness": liveness,
        "loudness": loudness,
        "mode": 1,
        "key": 0,
        "time_signature": 4,
        "genre": "Pop",
    }
    return features
