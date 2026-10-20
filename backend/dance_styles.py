"""Dance styles supported by DanceMinds and feature priors used for training."""

from __future__ import annotations

DANCE_STYLES = [
    {"category": "Indian Classical", "styles": ["Bharatanatyam", "Kathak", "Kuchipudi", "Odissi", "Manipuri", "Mohiniyattam", "Kathakali", "Sattriya"]},
    {"category": "Western", "styles": ["Ballet", "Contemporary", "Jazz", "Tap Dancing", "Hip-Hop", "Breakdancing", "Popping", "Locking", "House Dance"]},
    {"category": "Latin", "styles": ["Salsa", "Bachata", "Merengue", "Rumba", "Cha-cha-cha", "Samba", "Argentine Tango", "Paso Doble"]},
    {"category": "Ballroom", "styles": ["Waltz", "Foxtrot", "Quickstep", "Viennese Waltz", "Tango", "Slow Foxtrot"]},
    {"category": "Folk & Traditional", "styles": ["Bhangra", "Garba", "Kalbelia", "Flamenco", "Irish Step Dancing", "Morris Dancing", "Cossack Dance", "Belly Dance"]},
    {"category": "Modern & Street", "styles": ["Krump", "Waacking", "Voguing", "Afrobeats", "K-Pop Choreography", "Commercial Dance", "Urban Dance"]},
    {"category": "Cultural", "styles": ["Bollywood", "Chinese Classical", "Japanese Butoh", "African Traditional", "Middle Eastern", "Polynesian", "Native American"]},
]

STYLE_BY_NAME = {s: c for group in DANCE_STYLES for c in [group["category"]] for s in group["styles"]}
ALL_STYLES = [s for group in DANCE_STYLES for s in group["styles"]]

# Baseline musical profiles used to synthesize training examples. Values are
# (center, standard deviation) for a normal distribution, clipped to a sane
# musical range. These are informative priors; replace with measured audio
# features from a labelled corpus for production accuracy.
CATEGORY_PROFILE = {
    "Indian Classical": dict(tempo=(95, 12), energy=(0.55, 0.10), valence=(0.45, 0.12), danceability=(0.58, 0.10), acousticness=(0.72, 0.10), speechiness=(0.03, 0.02), instrumentalness=(0.60, 0.12), loudness=(-12, 2.5)),
    "Western": dict(tempo=(105, 18), energy=(0.62, 0.12), valence=(0.50, 0.14), danceability=(0.62, 0.12), acousticness=(0.35, 0.15), speechiness=(0.06, 0.03), instrumentalness=(0.25, 0.15), loudness=(-9, 2.0)),
    "Latin": dict(tempo=(165, 25), energy=(0.78, 0.10), valence=(0.72, 0.12), danceability=(0.86, 0.07), acousticness=(0.15, 0.08), speechiness=(0.05, 0.03), instrumentalness=(0.10, 0.08), loudness=(-7, 1.8)),
    "Ballroom": dict(tempo=(135, 30), energy=(0.60, 0.10), valence=(0.55, 0.12), danceability=(0.70, 0.10), acousticness=(0.25, 0.12), speechiness=(0.04, 0.02), instrumentalness=(0.15, 0.10), loudness=(-10, 2.0)),
    "Folk & Traditional": dict(tempo=(140, 22), energy=(0.70, 0.12), valence=(0.65, 0.13), danceability=(0.78, 0.10), acousticness=(0.45, 0.15), speechiness=(0.05, 0.03), instrumentalness=(0.30, 0.15), loudness=(-9, 2.0)),
    "Modern & Street": dict(tempo=(115, 18), energy=(0.82, 0.09), valence=(0.60, 0.14), danceability=(0.82, 0.08), acousticness=(0.08, 0.06), speechiness=(0.10, 0.05), instrumentalness=(0.05, 0.05), loudness=(-6, 1.6)),
    "Cultural": dict(tempo=(120, 22), energy=(0.66, 0.12), valence=(0.60, 0.14), danceability=(0.70, 0.12), acousticness=(0.40, 0.18), speechiness=(0.06, 0.03), instrumentalness=(0.35, 0.18), loudness=(-9, 2.0)),
}

# Per-style tempo / energy nudges refining the category baseline.
STYLE_NUDGE = {
    "Ballet": dict(tempo=(-25, 0.7), energy=(-0.15, 1.0), acousticness=(0.10, 1.0)),
    "Hip-Hop": dict(tempo=(-10, 1.0), energy=(0.08, 1.0), danceability=(0.08, 1.0), speechiness=(0.06, 1.0)),
    "Salsa": dict(tempo=(30, 1.0), energy=(0.08, 1.0), danceability=(0.10, 1.0)),
    "Samba": dict(tempo=(45, 1.0), energy=(0.08, 1.0)),
    "Waltz": dict(tempo=(-45, 1.0), energy=(-0.12, 1.0), danceability=(-0.06, 1.0)),
    "Quickstep": dict(tempo=(45, 1.0), energy=(0.05, 1.0)),
    "Bhangra": dict(tempo=(20, 1.0), energy=(0.10, 1.0)),
    "K-Pop Choreography": dict(tempo=(5, 1.0), energy=(0.10, 1.0), danceability=(0.10, 1.0)),
    "Bollywood": dict(tempo=(10, 1.0), energy=(0.08, 1.0), valence=(0.10, 1.0)),
    "Afrobeats": dict(tempo=(-10, 1.0), energy=(0.08, 1.0), valence=(0.10, 1.0)),
    "Japanese Butoh": dict(tempo=(-50, 1.0), energy=(-0.25, 1.0), danceability=(-0.20, 1.0)),
    "Breakdancing": dict(tempo=(0, 1.0), energy=(0.12, 1.0), danceability=(0.08, 1.0)),
}
