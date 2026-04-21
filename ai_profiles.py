from __future__ import annotations

from math import fabs

PROFILE_SETTINGS = {
    "support_large_audio": {
        "font_size": 30,
        "spacing": 2.2,
        "theme": "Soft Pastel",
        "tts_enabled": True,
        "voice_enabled": True,
        "tts_speed": 145,
        "font_style": "Open and Clear",
        "reading_width": "Narrow",
        "focus_mode": True,
        "chunking_mode": "Shorter Paragraphs",
        "title": "Support Large Audio",
        "description": "Bigger text, calmer layout, slower speech, and stronger support.",
    },
    "focus_high_spacing": {
        "font_size": 26,
        "spacing": 2.0,
        "theme": "Cool Blue",
        "tts_enabled": True,
        "voice_enabled": False,
        "tts_speed": 155,
        "font_style": "Open and Clear",
        "reading_width": "Narrow",
        "focus_mode": True,
        "chunking_mode": "Shorter Paragraphs",
        "title": "Focus High Spacing",
        "description": "Narrower reading area with clearer spacing and strong visual focus.",
    },
    "balanced_default": {
        "font_size": 22,
        "spacing": 1.6,
        "theme": "Bright",
        "tts_enabled": True,
        "voice_enabled": False,
        "tts_speed": 165,
        "font_style": "Simple",
        "reading_width": "Normal",
        "focus_mode": False,
        "chunking_mode": "Full Text",
        "title": "Balanced Default",
        "description": "A steady middle-ground profile for general use.",
    },
    "calm_low_stimulation": {
        "font_size": 24,
        "spacing": 1.9,
        "theme": "Warm Pink",
        "tts_enabled": True,
        "voice_enabled": False,
        "tts_speed": 150,
        "font_style": "Rounded",
        "reading_width": "Normal",
        "focus_mode": False,
        "chunking_mode": "Shorter Paragraphs",
        "title": "Calm Low Stimulation",
        "description": "Softer pacing and gentler visuals for a calmer reading feel.",
    },
    "independent_wide": {
        "font_size": 20,
        "spacing": 1.5,
        "theme": "Bright",
        "tts_enabled": False,
        "voice_enabled": False,
        "tts_speed": 175,
        "font_style": "Simple",
        "reading_width": "Wide",
        "focus_mode": False,
        "chunking_mode": "Full Text",
        "title": "Independent Wide",
        "description": "Less support and a wider reading area for stronger independent readers.",
    },
    "audio_guided": {
        "font_size": 28,
        "spacing": 2.1,
        "theme": "Cool Blue",
        "tts_enabled": True,
        "voice_enabled": True,
        "tts_speed": 135,
        "font_style": "Open and Clear",
        "reading_width": "Narrow",
        "focus_mode": True,
        "chunking_mode": "Shorter Paragraphs",
        "title": "Audio Guided",
        "description": "Built around stronger spoken support and slower audio guidance.",
    },
    "memory_support": {
        "font_size": 25,
        "spacing": 2.0,
        "theme": "Soft Pastel",
        "tts_enabled": True,
        "voice_enabled": False,
        "tts_speed": 150,
        "font_style": "Open and Clear",
        "reading_width": "Narrow",
        "focus_mode": True,
        "chunking_mode": "Shorter Paragraphs",
        "title": "Memory Support",
        "description": "Chunked reading support for readers who lose track of what they just read.",
    },
    "fatigue_relief": {
        "font_size": 26,
        "spacing": 2.0,
        "theme": "Warm Pink",
        "tts_enabled": True,
        "voice_enabled": False,
        "tts_speed": 150,
        "font_style": "Rounded",
        "reading_width": "Normal",
        "focus_mode": False,
        "chunking_mode": "Shorter Paragraphs",
        "title": "Fatigue Relief",
        "description": "A softer setup for readers whose eyes or head get tired on screen.",
    },
    "high_contrast_focus": {
        "font_size": 25,
        "spacing": 2.1,
        "theme": "High Contrast",
        "tts_enabled": False,
        "voice_enabled": False,
        "tts_speed": 165,
        "font_style": "Open and Clear",
        "reading_width": "Narrow",
        "focus_mode": True,
        "chunking_mode": "Shorter Paragraphs",
        "title": "High Contrast Focus",
        "description": "Stronger visual separation with a tighter reading focus.",
    },
    "light_audio_support": {
        "font_size": 23,
        "spacing": 1.7,
        "theme": "Bright",
        "tts_enabled": True,
        "voice_enabled": False,
        "tts_speed": 155,
        "font_style": "Simple",
        "reading_width": "Normal",
        "focus_mode": False,
        "chunking_mode": "Full Text",
        "title": "Light Audio Support",
        "description": "A lighter reading setup with audio available but not overly heavy.",
    },
}


def profile_title(profile_label: str) -> str:
    return PROFILE_SETTINGS.get(profile_label, PROFILE_SETTINGS["balanced_default"])["title"]


def profile_description(profile_label: str) -> str:
    return PROFILE_SETTINGS.get(profile_label, PROFILE_SETTINGS["balanced_default"])["description"]


def apply_profile_to_state(profile_label: str, state):
    profile = PROFILE_SETTINGS.get(profile_label, PROFILE_SETTINGS["balanced_default"])

    # I kept this in one place so the model and the UI both use the same profile setup.
    for key in [
        "font_size",
        "spacing",
        "theme",
        "tts_enabled",
        "voice_enabled",
        "tts_speed",
        "font_style",
        "reading_width",
        "focus_mode",
        "chunking_mode",
    ]:
        state[key] = profile[key]

    state["current_profile_label"] = profile_label


def profile_distance(settings: dict, profile_label: str) -> float:
    profile = PROFILE_SETTINGS[profile_label]

    score = 0.0
    score += fabs(float(settings["font_size"]) - float(profile["font_size"])) / 10
    score += fabs(float(settings["spacing"]) - float(profile["spacing"])) * 2
    score += fabs(float(settings["tts_speed"]) - float(profile["tts_speed"])) / 40

    for key in ["theme", "font_style", "reading_width", "chunking_mode"]:
        if settings[key] != profile[key]:
            score += 1.0

    for key in ["focus_mode", "tts_enabled", "voice_enabled"]:
        if bool(settings[key]) != bool(profile[key]):
            score += 1.0

    return score


def closest_profile_from_settings(settings: dict) -> str:
    labels = list(PROFILE_SETTINGS.keys())
    labels.sort(key=lambda label: profile_distance(settings, label))
    return labels[0]


def compute_success_score(feedback: dict) -> float:
    numeric_fields = [
        "ease",
        "support",
        "enjoyment",
        "font_comfort",
        "spacing_comfort",
        "theme_helpfulness",
        "voice_speed_comfort",
        "audio_helpfulness",
        "setup_match",
    ]
    base_values = [int(feedback[field]) for field in numeric_fields]
    base_score = sum(base_values) / len(base_values)

    recommendation_bonus = {
        "Yes": 0.3,
        "Maybe": 0.1,
        "No": -0.2,
        "No response": 0.0,
    }.get(feedback.get("recommend", "No response"), 0.0)

    memory_bonus = {
        "Yes": 0.2,
        "Maybe": 0.1,
        "No": -0.1,
        "No response": 0.0,
    }.get(feedback.get("would_remember", "No response"), 0.0)

    return round(max(1.0, min(5.0, base_score + recommendation_bonus + memory_bonus)), 2)