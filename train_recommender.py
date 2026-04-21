import argparse
import random
from datetime import datetime, timezone

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ai_profiles import PROFILE_SETTINGS
from ai_recommender import (
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    MODEL_PATH,
    NUMERIC_FEATURES,
)
from database import get_training_dataframe, init_db


def bootstrap_training_rows(row_count: int = 1000) -> pd.DataFrame:
    rng = random.Random(42)
    rows = []

    # I added starter patterns for all 10 profiles so the model can learn the full set in one go.
    profile_rules = {
        "support_large_audio": {
            "difficulty": ["Severe", "Moderate"],
            "confidence": (1, 3),
            "comprehension": (1, 3),
            "speed": (70, 120),
            "keep_place": (4, 5),
            "crowded_text": (4, 5),
            "screen_tiredness": (3, 5),
            "memory_after_reading": (1, 2),
            "likes_read_aloud": (5, 5),
            "likes_short_chunks": (4, 5),
            "likes_calm_colours": (4, 5),
            "auto_adjust_ok": 1,
            "tts_enabled": 1,
            "voice_enabled": 1,
        },
        "focus_high_spacing": {
            "difficulty": ["Moderate"],
            "confidence": (4, 7),
            "comprehension": (4, 7),
            "speed": (100, 160),
            "keep_place": (4, 5),
            "crowded_text": (4, 5),
            "screen_tiredness": (2, 4),
            "memory_after_reading": (2, 4),
            "likes_read_aloud": (2, 4),
            "likes_short_chunks": (4, 5),
            "likes_calm_colours": (2, 4),
            "auto_adjust_ok": 1,
            "tts_enabled": 1,
            "voice_enabled": 0,
        },
        "balanced_default": {
            "difficulty": ["Moderate", "Mild"],
            "confidence": (5, 8),
            "comprehension": (5, 8),
            "speed": (120, 190),
            "keep_place": (2, 3),
            "crowded_text": (2, 3),
            "screen_tiredness": (2, 3),
            "memory_after_reading": (3, 4),
            "likes_read_aloud": (2, 3),
            "likes_short_chunks": (2, 3),
            "likes_calm_colours": (2, 3),
            "auto_adjust_ok": 1,
            "tts_enabled": 1,
            "voice_enabled": 0,
        },
        "calm_low_stimulation": {
            "difficulty": ["Moderate", "Mild"],
            "confidence": (4, 7),
            "comprehension": (4, 7),
            "speed": (90, 150),
            "keep_place": (3, 4),
            "crowded_text": (3, 4),
            "screen_tiredness": (4, 5),
            "memory_after_reading": (2, 4),
            "likes_read_aloud": (2, 4),
            "likes_short_chunks": (3, 5),
            "likes_calm_colours": (4, 5),
            "auto_adjust_ok": 1,
            "tts_enabled": 1,
            "voice_enabled": 0,
        },
        "independent_wide": {
            "difficulty": ["Mild"],
            "confidence": (8, 10),
            "comprehension": (8, 10),
            "speed": (180, 260),
            "keep_place": (1, 2),
            "crowded_text": (1, 2),
            "screen_tiredness": (1, 2),
            "memory_after_reading": (4, 5),
            "likes_read_aloud": (1, 2),
            "likes_short_chunks": (1, 2),
            "likes_calm_colours": (1, 2),
            "auto_adjust_ok": 1,
            "tts_enabled": 0,
            "voice_enabled": 0,
        },
        "audio_guided": {
            "difficulty": ["Severe", "Moderate"],
            "confidence": (1, 5),
            "comprehension": (1, 5),
            "speed": (70, 120),
            "keep_place": (3, 5),
            "crowded_text": (3, 5),
            "screen_tiredness": (2, 4),
            "memory_after_reading": (1, 3),
            "likes_read_aloud": (5, 5),
            "likes_short_chunks": (4, 5),
            "likes_calm_colours": (2, 4),
            "auto_adjust_ok": 1,
            "tts_enabled": 1,
            "voice_enabled": 1,
        },
        "memory_support": {
            "difficulty": ["Moderate"],
            "confidence": (3, 6),
            "comprehension": (3, 5),
            "speed": (100, 150),
            "keep_place": (3, 4),
            "crowded_text": (2, 4),
            "screen_tiredness": (2, 4),
            "memory_after_reading": (1, 2),
            "likes_read_aloud": (3, 4),
            "likes_short_chunks": (4, 5),
            "likes_calm_colours": (3, 4),
            "auto_adjust_ok": 1,
            "tts_enabled": 1,
            "voice_enabled": 0,
        },
        "fatigue_relief": {
            "difficulty": ["Moderate", "Mild"],
            "confidence": (4, 7),
            "comprehension": (4, 7),
            "speed": (90, 150),
            "keep_place": (2, 4),
            "crowded_text": (2, 4),
            "screen_tiredness": (5, 5),
            "memory_after_reading": (2, 4),
            "likes_read_aloud": (2, 3),
            "likes_short_chunks": (3, 4),
            "likes_calm_colours": (4, 5),
            "auto_adjust_ok": 1,
            "tts_enabled": 1,
            "voice_enabled": 0,
        },
        "high_contrast_focus": {
            "difficulty": ["Moderate"],
            "confidence": (4, 7),
            "comprehension": (4, 7),
            "speed": (100, 160),
            "keep_place": (4, 5),
            "crowded_text": (5, 5),
            "screen_tiredness": (2, 4),
            "memory_after_reading": (2, 4),
            "likes_read_aloud": (1, 3),
            "likes_short_chunks": (4, 5),
            "likes_calm_colours": (1, 2),
            "auto_adjust_ok": 1,
            "tts_enabled": 0,
            "voice_enabled": 0,
        },
        "light_audio_support": {
            "difficulty": ["Mild", "Moderate"],
            "confidence": (5, 8),
            "comprehension": (5, 8),
            "speed": (110, 180),
            "keep_place": (2, 3),
            "crowded_text": (2, 3),
            "screen_tiredness": (2, 3),
            "memory_after_reading": (3, 4),
            "likes_read_aloud": (4, 5),
            "likes_short_chunks": (2, 3),
            "likes_calm_colours": (2, 3),
            "auto_adjust_ok": 1,
            "tts_enabled": 1,
            "voice_enabled": 0,
        },
    }

    labels = list(PROFILE_SETTINGS.keys())

    for _ in range(row_count):
        target = rng.choice(labels)
        rule = profile_rules[target]
        session_count = rng.randint(0, 12)
        avg_base = 3.3 if target in {"balanced_default", "independent_wide", "light_audio_support"} else 3.7

        rows.append(
            {
                "difficulty": rng.choice(rule["difficulty"]),
                "confidence": rng.randint(*rule["confidence"]),
                "comprehension": rng.randint(*rule["comprehension"]),
                "speed": rng.randint(*rule["speed"]),
                "keep_place": rng.randint(*rule["keep_place"]),
                "crowded_text": rng.randint(*rule["crowded_text"]),
                "screen_tiredness": rng.randint(*rule["screen_tiredness"]),
                "memory_after_reading": rng.randint(*rule["memory_after_reading"]),
                "likes_read_aloud": rng.randint(*rule["likes_read_aloud"]),
                "likes_short_chunks": rng.randint(*rule["likes_short_chunks"]),
                "likes_calm_colours": rng.randint(*rule["likes_calm_colours"]),
                "auto_adjust_ok": rule["auto_adjust_ok"],
                "tts_enabled": rule["tts_enabled"],
                "voice_enabled": rule["voice_enabled"],
                "hist_session_count": session_count,
                "hist_avg_ease": round(rng.uniform(avg_base - 0.8, avg_base + 0.8), 2),
                "hist_avg_support": round(rng.uniform(avg_base - 0.8, avg_base + 0.8), 2),
                "hist_avg_enjoyment": round(rng.uniform(avg_base - 0.7, avg_base + 0.7), 2),
                "hist_avg_setup_match": round(rng.uniform(avg_base - 0.6, avg_base + 0.8), 2),
                "hist_avg_setting_changes": round(rng.uniform(0, 4 if session_count else 0.5), 2),
                "hist_last_profile": target if session_count > 0 and rng.random() > 0.35 else "none",
                "target": target,
            }
        )

    return pd.DataFrame(rows)


def build_preprocessor():
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("categorical", categorical_transformer, CATEGORICAL_FEATURES),
            ("numeric", numeric_transformer, NUMERIC_FEATURES),
        ]
    )


def build_candidate_models():
    preprocessor = build_preprocessor()

    return {
        "logistic_regression": Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", LogisticRegression(max_iter=2500)),
            ]
        ),
        "random_forest": Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", RandomForestClassifier(n_estimators=350, random_state=42, min_samples_leaf=2)),
            ]
        ),
        "mlp_classifier": Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", MLPClassifier(hidden_layer_sizes=(96, 48), max_iter=1500, random_state=42)),
            ]
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap", type=int, default=0, help="Add bootstrap rows before training")
    args = parser.parse_args()

    init_db()
    real_data = get_training_dataframe(min_success_score=3.0)
    frames = []

    if not real_data.empty:
        frames.append(real_data)

    bootstrap_size = args.bootstrap
    if len(real_data) < 100 and bootstrap_size == 0:
        bootstrap_size = 1000

    if bootstrap_size > 0:
        frames.append(bootstrap_training_rows(bootstrap_size))

    if not frames:
        raise SystemExit("No training data was found. Collect sessions first or use --bootstrap.")

    dataset = pd.concat(frames, ignore_index=True).dropna(subset=["target"]).copy()

    X = dataset[FEATURE_COLUMNS]
    y = dataset["target"]

    class_counts = y.value_counts()
    stratify_target = y if class_counts.min() >= 2 else None

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=stratify_target,
    )

    candidates = build_candidate_models()
    best_name = ""
    best_model = None
    best_score = -1.0
    all_scores = {}

    for model_name, pipeline in candidates.items():
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)

        accuracy = accuracy_score(y_test, predictions)
        weighted_f1 = f1_score(y_test, predictions, average="weighted")
        all_scores[model_name] = {
            "accuracy": round(float(accuracy), 4),
            "weighted_f1": round(float(weighted_f1), 4),
        }

        print(f"\n{model_name}")
        print(f"accuracy: {accuracy:.4f}")
        print(f"weighted_f1: {weighted_f1:.4f}")
        print(classification_report(y_test, predictions, zero_division=0))

        if weighted_f1 > best_score:
            best_score = weighted_f1
            best_name = model_name
            best_model = pipeline

    if best_model is None:
        raise SystemExit("Training did not produce a usable model.")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        "model": best_model,
        "model_name": best_name,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "scores": all_scores,
        "feature_columns": FEATURE_COLUMNS,
    }
    joblib.dump(artifact, MODEL_PATH)

    print("\nSaved best model to:")
    print(MODEL_PATH)
    print(f"Best model: {best_name}")
    print(all_scores[best_name])


if __name__ == "__main__":
    main()