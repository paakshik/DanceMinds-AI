"""Generate a rich, readable choreography routine for a chosen dance style."""

from __future__ import annotations

import datetime
import math
import random
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from dance_styles import STYLE_BY_NAME

random.seed(42)

COMMON_STEP_META = {
    "Foundation and Warm-up": {
        "counts": "8 slow counts x 4",
        "focus": "Posture, breathing, weight placement and joint mobility",
        "cue": "Use a slow section of the song (intro/verse) to establish the groove.",
    },
    "Basic Movement Patterns": {
        "counts": "8 counts x 4",
        "focus": "Core step shapes, timing and weight transfers",
        "cue": "Lock into the main beat; keep steps small and accurate first.",
    },
    "Coordination Building": {
        "counts": "8 counts x 4",
        "focus": "Upper/lower body separation and musical accents",
        "cue": "Add arm lines only after the feet are confident.",
    },
    "Intermediate Techniques": {
        "counts": "8 counts x 4",
        "focus": "Turns, level changes, isolations or style-specific moves",
        "cue": "Practice these at half speed before full tempo.",
    },
    "Expression and Flow": {
        "counts": "16 counts x 2",
        "focus": "Facial expression, styling and smooth transitions",
        "cue": "Dance to the chorus or drop; perform, don’t just drill.",
    },
    "Complete Routine": {
        "counts": "Full song",
        "focus": "Endurance, memory and performance quality",
        "cue": "Run the full routine 3-4 times, resting between attempts.",
    },
}

VIDEO_TEMPLATES: Dict[str, List[Dict[str, str]]] = {
    "Bharatanatyam": [
        {"title": "Warm-up and Basic Position", "duration": "0:45", "description": "Begin with gentle stretches for ankles, knees and spine, then establish Araimandi (half-sitting) with heels together, toes apart, and a tall, lifted spine. Hold a steady gaze forward and practise slow knee bends to prepare the body for classical footwork."},
        {"title": "Namaskaram Sequence", "duration": "1:20", "description": "Perform the traditional greeting: bring palms together at the chest, then lower the hands gracefully while bending the knees. Expand into a wide, symmetrical reach with the arms, and return to center with control and a soft, devotional expression."},
        {"title": "Basic Adavu Patterns", "duration": "1:30", "description": "Practise Tatta and Natta adavus in place, striking the floor clearly with the foot while keeping the spine stable. Add alternating arm movements that move opposite to the stepping leg, and maintain a continuous rhythmic flow rather than stopping between repetitions."},
        {"title": "Mudra Integration", "duration": "1:15", "description": "Hold clear, classical hand gestures such as Pataka or Alapadma. Transition between mudras while walking on counts, letting the fingers stay firm but relaxed, and ensure the audience can read each shape from a distance."},
        {"title": "Expression and Abhinaya", "duration": "1:45", "description": "Add facial expression, neck movement and eye direction to each phrase. Practise telling a simple story with the face while the body stays rhythmically accurate, using eyebrow lifts, chin movements and glances that match the song’s mood."},
        {"title": "Complete Tillana", "duration": "2:30", "description": "Link all elements into a full rhythmic sequence: adavus, mudras, eye movement and strong foot stamping. End with a held final pose and a clear Namaskaram, making the finish look definitive and composed."},
    ],
    "Hip-Hop": [
        {"title": "Basic Groove Foundation", "duration": "0:50", "description": "Find the downbeat and practise a relaxed bounce in the knees and hips. Keep the chest upright, shoulders easy, and move the head subtly with the rhythm so the groove looks natural rather than forced."},
        {"title": "Isolation Techniques", "duration": "1:10", "description": "Isolate the head, shoulders, chest and hips one at a time on the beat. Keep everything else still, then combine two isolations into a small phrase while staying on tempo and keeping the movements sharp but controlled."},
        {"title": "Top Rock Basics", "duration": "1:25", "description": "Step forward, side and back with a bouncy groove, adding small arm swings and body rolls. Travel cleanly through space, turn the toes outward on direction changes, and keep the upper body relaxed and stylish."},
        {"title": "Breaking Fundamentals", "duration": "1:40", "description": "Practise six-step, CCs and basic freezes, keeping the weight centred and the transitions smooth. Work on controlled descents to the floor, then build up from the floor with a kick or sweep so the floorwork looks intentional."},
        {"title": "Freestyle Flow", "duration": "1:30", "description": "Improvisation drill: listen to the track and repeat your favourite two moves, then add one new variation each 8-count. Focus on confidence, musicality and recovery rather than perfection."},
        {"title": "Battle Ready Combo", "duration": "2:00", "description": "Finish with a hard-hitting combination: groove entrance, isolations, travel step, quick floorwork, freeze and an exit. Add attitude, level changes and one signature move so the routine looks performance-ready."},
    ],
    "Ballet": [
        {"title": "Barre Warm-up", "duration": "1:00", "description": "Begin with pliés, tendus and dégagés at the barre, keeping the spine lengthened and turnout gentle. Stretch calves, hamstrings and hips before leaving the barre so the centre work feels supported."},
        {"title": "Basic Positions", "duration": "1:15", "description": "Practise first through fifth positions of the feet with the corresponding arm positions. Check that the knees track over the toes, the weight is centred and the shoulders stay relaxed and open."},
        {"title": "Port de Bras", "duration": "1:20", "description": "Move the arms through first, second and fifth positions with long, sweeping lines. Let the fingers follow the arms, and keep the ribcage lifted while the hips and legs remain quiet and stable."},
        {"title": "Adagio Combinations", "duration": "1:45", "description": "Practise slow developpés, arabesques and balances, holding each shape for several counts. Keep transitions unrushed, lifting through the supporting leg, and use the breath to control timing."},
        {"title": "Allegro Preparations", "duration": "1:35", "description": "Work on small jumps such as sautés and échappés, starting with two-footed jumps before travelling. Land softly through the feet, bend the knees to absorb impact and keep the torso lifted."},
        {"title": "Grand Finale", "duration": "2:15", "description": "Link a travelling phrase of jetés or assemblés with turns and a final pose. Finish with a reverential bow, breathing steadily, so the ending feels elegant and complete."},
    ],
    "Salsa": [
        {"title": "Basic Salsa Step", "duration": "0:55", "description": "Step forward on 1, replace on 2, step back on 3, then pause on 4. Repeat in the opposite direction, staying on the balls of the feet and keeping the hips free but controlled."},
        {"title": "Cross Body Lead", "duration": "1:25", "description": "Lead or follow a travelling path across the line of dance: step forward, turn the shoulder, step through and replace. Keep the connection light and the movement rotational rather than pulling."},
        {"title": "Right and Left Turns", "duration": "1:30", "description": "Practise outside and inside turns for both partners, spotting the turn and keeping the feet under the body. Finish each turn by returning to the basic step with clear timing and posture."},
        {"title": "Shines and Footwork", "duration": "1:20", "description": "Add solo footwork variations such as suzy-q, heel-toe and cross steps. Keep the upper body calm, the arms stylish, and the footwork precise to the clave and bass."},
        {"title": "Advanced Combinations", "duration": "1:50", "description": "Link CBLs with multiple turns and styling, adding body rolls or arm styling. Practise slowly first so the follow stays comfortable and the lead stays balanced."},
        {"title": "Performance Routine", "duration": "2:20", "description": "Dance a full social sequence: basic, cross body lead, turns, shines and a playful ending. Add eye contact, styling and a clean pose on the final beat."},
    ],
}

DEFAULT_TEMPLATE = [
    {"title": "Foundation and Warm-up", "duration": "0:45", "description": "Begin with posture alignment, breathing and gentle full-body mobility. Move every major joint, find a comfortable bounce, and let the music set your tempo before attempting full choreography."},
    {"title": "Basic Movement Patterns", "duration": "1:15", "description": "Learn the essential step shapes of the chosen style. Keep movements small, counts clear and feet definite, repeating each pattern until the rhythm feels natural and repeatable."},
    {"title": "Coordination Building", "duration": "1:30", "description": "Combine arms and footwork while keeping the core stable. Practise layering one element at a time, and stop if movements become tense; reset and re-run slowly."},
    {"title": "Intermediate Techniques", "duration": "1:40", "description": "Add turns, level changes, sharper accents or style-specific moves. Work at half speed first, then build to full tempo while maintaining balance and clean lines."},
    {"title": "Expression and Flow", "duration": "1:25", "description": "Perform the sequence with musicality and emotion. Use the chorus or strongest beat for the most energetic moment, and smooth the transitions between phrases."},
    {"title": "Complete Routine", "duration": "2:30", "description": "Run the entire routine several times, tracking stamina, timing and memory. Cool down with easy stretching, and note two areas to improve in the next practice."},
]


def _meta_for(title: str) -> Dict[str, str]:
    meta = COMMON_STEP_META.get(title, {})
    return {
        "counts": meta.get("counts", "8 counts x 4"),
        "focus": meta.get("focus", "Technique, timing and control"),
        "cue": meta.get("cue", "Match the strongest beat and stay relaxed."),
    }


def _tailor_description(style: str, title: str, description: str, age: int, profession: str) -> (str, List[str]):
    notes: List[str] = []
    tailored = description
    if age and age < 13:
        tailored += " Keep directions simple, use playful imagery, and take water breaks every 5 minutes."
        notes.append("Child-friendly pacing: short explanations and frequent breaks.")
    elif age and age >= 60:
        tailored += " Use a supported, low-impact version, keep the spine tall and reduce jump height."
        notes.append("Older-adult safety: prioritise balance, small steps and controlled range.")
    if profession:
        p = profession.lower()
        if "teacher" in p or "instructor" in p:
            notes.append("Teaching note: demonstrate slowly first, then let learners mirror.")
        elif "professional" in p or "dancer" in p:
            notes.append("Performance note: add stylistic variations and sharper accents.")
        elif "student" in p:
            notes.append("Learning note: repeat each 8-count 3 times before moving on.")
        elif "beginner" in p:
            notes.append("Beginner note: reduce speed and simplify arm lines.")
    return tailored, notes


def generate_video_steps(style: str, age: int, profession: str) -> List[Dict[str, Any]]:
    template = VIDEO_TEMPLATES.get(style, DEFAULT_TEMPLATE)
    steps: List[Dict[str, Any]] = []
    for i, step in enumerate(template):
        meta = _meta_for(step["title"])
        tailored, notes = _tailor_description(style, step["title"], step["description"], age, profession)
        steps.append({
            "order": i + 1,
            "title": step["title"],
            "duration": step["duration"],
            "counts": meta["counts"],
            "focus": meta["focus"],
            "musicCue": meta["cue"],
            "description": tailored,
            "coachTip": " ".join(notes) if notes else "General practice guidance.",
        })
    return steps


def format_duration(seconds: int) -> str:
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins}:{secs:02d}"


def parse_duration(value: str) -> int:
    parts = value.split(":")
    mins = int(parts[0]) if parts and parts[0].isdigit() else 0
    secs = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return mins * 60 + secs


def analyze_music(features: Optional[Dict[str, Any]] = None, song_title: Optional[str] = None) -> Dict[str, Any]:
    if features and "tempo" in features:
        bpm = int(round(float(features["tempo"])))
        energy = int(round(float(features.get("energy", 0.6)) * 100))
        genre = str(features.get("genre", "Pop"))
    else:
        bpm = random.randint(90, 150)
        energy = random.randint(45, 85)
        genre = random.choice(["Pop", "Hip-Hop", "Jazz", "Electronic", "Folk"])
    duration_seconds = random.randint(160, 300)
    return {
        "bpm": max(40, min(240, bpm)),
        "durationSeconds": duration_seconds,
        "durationLabel": format_duration(duration_seconds),
        "energy": max(0, min(100, energy)),
        "genre": genre,
        "title": song_title or (features or {}).get("title") or "Unknown track",
    }


def build_choreography_payload(
    *,
    dance_style: str,
    age: int,
    height: str,
    profession: str,
    video_quality: str = "720p",
    features: Optional[Dict[str, Any]] = None,
    song_title: Optional[str] = None,
) -> Dict[str, Any]:
    quality_options = ["1080p", "720p", "480p"]
    if video_quality not in quality_options:
        video_quality = "720p"
    safe_age = max(5, min(100, int(age) if age is not None else 18))

    analysis = analyze_music(features, song_title)
    steps = generate_video_steps(dance_style, safe_age, profession or "")
    total_seconds = sum(parse_duration(s["duration"]) for s in steps)

    category = STYLE_BY_NAME.get(dance_style, "General")

    return {
        "id": str(uuid.uuid4()),
        "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "music": {
            "title": analysis["title"],
            "duration": analysis["durationLabel"],
            "bpm": analysis["bpm"],
            "genre": analysis["genre"],
            "energy": analysis["energy"],
        },
        "request": {
            "danceStyle": dance_style,
            "category": category,
            "age": safe_age,
            "height": height,
            "profession": profession,
            "videoQuality": video_quality,
        },
        "summary": {
            "totalVideos": len(steps),
            "totalDurationSeconds": total_seconds,
            "totalDurationLabel": format_duration(total_seconds),
            "insights": [
                f"Recommended practising '{steps[0]['title'].lower()}' for 5 minutes",
                f"Focus on transitions between steps {max(1, len(steps)//2)} and {max(2, len(steps)//2 + 1)}",
            ],
            "ageNote": "Gentle pacing used (under 13)" if safe_age < 13 else ("Low-impact focus (60+)" if safe_age >= 60 else "Standard pacing"),
            "professionNote": (profession or "General").strip(),
        },
        "videoSteps": steps,
    }
