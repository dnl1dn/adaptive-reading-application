from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

FEATURE_COLUMNS = [
    "difficulty",
    "confidence",
    "comprehension",
    "speed",
    "keep_place",
    "crowded_text",
    "screen_tiredness",
    "memory_after_reading",
    "likes_read_aloud",
    "likes_short_chunks",
    "likes_calm_colours",
    "auto_adjust_ok",
    "tts_enabled",
    "voice_enabled",
    "hist_session_count",
    "hist_avg_ease",
    "hist_avg_support",
    "hist_avg_enjoyment",
    "hist_avg_setup_match",
    "hist_avg_setting_changes",
    "hist_last_profile",
]

CATEGORICAL_FEATURES = ["difficulty", "hist_last_profile"]
NUMERIC_FEATURES = [
    "confidence",
    "comprehension",
    "speed",
    "keep_place",
    "crowded_text",
    "screen_tiredness",
    "memory_after_reading",
    "likes_read_aloud",
    "likes_short_chunks",
    "likes_calm_colours",
    "auto_adjust_ok",
    "tts_enabled",
    "voice_enabled",
    "hist_session_count",
    "hist_avg_ease",
    "hist_avg_support",
    "hist_avg_enjoyment",
    "hist_avg_setup_match",
    "hist_avg_setting_changes",
]

MODEL_PATH = Path(__file__).resolve().parent / "models" / "reading_recommender.joblib"


def build_feature_row(assessment: dict, history: dict | None = None) -> dict:
    history = history or {}

    return {
        "difficulty": assessment.get("difficulty", "Moderate"),
        "confidence": int(assessment.get("confidence", 5)),
        "comprehension": int(assessment.get("comprehension", 5)),
        "speed": int(assessment.get("speed", 140)),
        "keep_place": int(assessment.get("keep_place", 3)),
        "crowded_text": int(assessment.get("crowded_text", 3)),
        "screen_tiredness": int(assessment.get("screen_tiredness", 3)),
        "memory_after_reading": int(assessment.get("memory_after_reading", 3)),
        "likes_read_aloud": int(assessment.get("likes_read_aloud", 3)),
        "likes_short_chunks": int(assessment.get("likes_short_chunks", 3)),
        "likes_calm_colours": int(assessment.get("likes_calm_colours", 3)),
        "auto_adjust_ok": int(bool(assessment.get("auto_adjust_ok", True))),
        "tts_enabled": int(bool(assessment.get("tts_enabled", True))),
        "voice_enabled": int(bool(assessment.get("voice_enabled", False))),
        "hist_session_count": int(history.get("session_count", 0)),
        "hist_avg_ease": float(history.get("avg_ease", 0)),
        "hist_avg_support": float(history.get("avg_support", 0)),
        "hist_avg_enjoyment": float(history.get("avg_enjoyment", 0)),
        "hist_avg_setup_match": float(history.get("avg_setup_match", 0)),
        "hist_avg_setting_changes": float(history.get("avg_setting_changes", 0)),
        "hist_last_profile": history.get("last_profile", "none") or "none",
    }


@lru_cache(maxsize=1)
def load_model_artifact():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


def model_is_available() -> bool:
    return MODEL_PATH.exists()


def get_model_details() -> dict | None:
    artifact = load_model_artifact()
    if not artifact:
        return None

    return {
        "model_name": artifact.get("model_name", "Unknown"),
        "trained_at": artifact.get("trained_at", "Unknown"),
        "scores": artifact.get("scores", {}),
    }


def recommend_profile(assessment: dict, history: dict | None, fallback_profile: str) -> dict:
    artifact = load_model_artifact()
    if not artifact:
        return {
            "profile": fallback_profile,
            "source": "baseline rules",
            "model_name": "None",
            "confidence": None,
        }

    feature_row = build_feature_row(assessment, history)
    feature_frame = pd.DataFrame([feature_row], columns=FEATURE_COLUMNS)
    model = artifact["model"]

    prediction = model.predict(feature_frame)[0]
    confidence = None

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(feature_frame)[0]
        confidence = round(float(probabilities.max()), 3)

    return {
        "profile": prediction,
        "source": f'trained model ({artifact.get("model_name", "Unknown")})',
        "model_name": artifact.get("model_name", "Unknown"),
        "confidence": confidence,
    }