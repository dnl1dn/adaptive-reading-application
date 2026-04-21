from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).resolve().parent / "brightpath.db"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def to_int(value) -> int:
    return 1 if bool(value) else 0


def init_db():
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                last_login TEXT NOT NULL,
                study_consent INTEGER NOT NULL DEFAULT 0,
                assessment_completed INTEGER NOT NULL DEFAULT 0,
                difficulty TEXT NOT NULL DEFAULT 'Moderate',
                confidence INTEGER NOT NULL DEFAULT 5,
                comprehension INTEGER NOT NULL DEFAULT 5,
                speed INTEGER NOT NULL DEFAULT 140,
                keep_place INTEGER NOT NULL DEFAULT 3,
                crowded_text INTEGER NOT NULL DEFAULT 3,
                screen_tiredness INTEGER NOT NULL DEFAULT 3,
                memory_after_reading INTEGER NOT NULL DEFAULT 3,
                likes_read_aloud INTEGER NOT NULL DEFAULT 3,
                likes_short_chunks INTEGER NOT NULL DEFAULT 3,
                likes_calm_colours INTEGER NOT NULL DEFAULT 3,
                auto_adjust_ok INTEGER NOT NULL DEFAULT 1,
                font_size INTEGER NOT NULL DEFAULT 22,
                spacing REAL NOT NULL DEFAULT 1.6,
                theme TEXT NOT NULL DEFAULT 'Bright',
                tts_enabled INTEGER NOT NULL DEFAULT 1,
                voice_enabled INTEGER NOT NULL DEFAULT 0,
                tts_speed INTEGER NOT NULL DEFAULT 165,
                font_style TEXT NOT NULL DEFAULT 'Simple',
                reading_width TEXT NOT NULL DEFAULT 'Normal',
                focus_mode INTEGER NOT NULL DEFAULT 0,
                chunking_mode TEXT NOT NULL DEFAULT 'Full Text',
                ai_mode TEXT NOT NULL DEFAULT 'Balanced Support',
                reading_profile TEXT NOT NULL DEFAULT 'Balanced Reader',
                current_profile_label TEXT NOT NULL DEFAULT 'balanced_default'
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                recommended_profile TEXT,
                recommended_by_ai INTEGER NOT NULL DEFAULT 0,
                baseline_profile TEXT,

                difficulty TEXT,
                confidence INTEGER,
                comprehension INTEGER,
                speed INTEGER,
                keep_place INTEGER,
                crowded_text INTEGER,
                screen_tiredness INTEGER,
                memory_after_reading INTEGER,
                likes_read_aloud INTEGER,
                likes_short_chunks INTEGER,
                likes_calm_colours INTEGER,
                auto_adjust_ok INTEGER,
                tts_enabled INTEGER,
                voice_enabled INTEGER,

                hist_session_count INTEGER DEFAULT 0,
                hist_avg_ease REAL DEFAULT 0,
                hist_avg_support REAL DEFAULT 0,
                hist_avg_enjoyment REAL DEFAULT 0,
                hist_avg_setup_match REAL DEFAULT 0,
                hist_avg_setting_changes REAL DEFAULT 0,
                hist_last_profile TEXT DEFAULT 'none',

                font_size_start INTEGER,
                spacing_start REAL,
                theme_start TEXT,
                font_style_start TEXT,
                reading_width_start TEXT,
                focus_mode_start INTEGER,
                chunking_mode_start TEXT,
                tts_speed_start INTEGER,

                audio_used INTEGER DEFAULT 0,
                custom_tts_used INTEGER DEFAULT 0,
                setting_changes INTEGER DEFAULT 0,

                font_size_final INTEGER,
                spacing_final REAL,
                theme_final TEXT,
                font_style_final TEXT,
                reading_width_final TEXT,
                focus_mode_final INTEGER,
                chunking_mode_final TEXT,
                tts_speed_final INTEGER,

                ease INTEGER,
                support INTEGER,
                enjoyment INTEGER,
                font_comfort INTEGER,
                spacing_comfort INTEGER,
                theme_helpfulness INTEGER,
                voice_speed_comfort INTEGER,
                audio_helpfulness INTEGER,
                setup_match INTEGER,
                would_remember TEXT,
                recommend TEXT,
                comments TEXT,
                changed_settings_reason TEXT,

                final_profile_label TEXT,
                success_score REAL,
                accepted_recommendation INTEGER DEFAULT 0,

                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        connection.commit()


def list_users() -> list[str]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT username FROM users ORDER BY LOWER(username) ASC"
        ).fetchall()
    return [row["username"] for row in rows]


def get_user_by_username(username: str) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE LOWER(username) = LOWER(?)",
            (username,),
        ).fetchone()
    return dict(row) if row else None


def create_user(username: str, study_consent: bool) -> dict:
    existing = get_user_by_username(username)
    if existing:
        raise ValueError("That profile name already exists.")

    created_at = utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO users (
                username,
                created_at,
                last_login,
                study_consent
            )
            VALUES (?, ?, ?, ?)
            """,
            (username, created_at, created_at, to_int(study_consent)),
        )
        connection.commit()

    user = get_user_by_username(username)
    if not user:
        raise ValueError("The new profile could not be created.")
    return user


def update_last_login(user_id: int):
    with get_connection() as connection:
        connection.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (utc_now(), user_id),
        )
        connection.commit()


def save_user_profile(
    user_id: int,
    assessment: dict,
    settings: dict,
    ai_mode: str,
    reading_profile: str,
    current_profile_label: str,
):
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE users
            SET
                assessment_completed = 1,
                difficulty = ?,
                confidence = ?,
                comprehension = ?,
                speed = ?,
                keep_place = ?,
                crowded_text = ?,
                screen_tiredness = ?,
                memory_after_reading = ?,
                likes_read_aloud = ?,
                likes_short_chunks = ?,
                likes_calm_colours = ?,
                auto_adjust_ok = ?,
                font_size = ?,
                spacing = ?,
                theme = ?,
                tts_enabled = ?,
                voice_enabled = ?,
                tts_speed = ?,
                font_style = ?,
                reading_width = ?,
                focus_mode = ?,
                chunking_mode = ?,
                ai_mode = ?,
                reading_profile = ?,
                current_profile_label = ?
            WHERE id = ?
            """,
            (
                assessment["difficulty"],
                int(assessment["confidence"]),
                int(assessment["comprehension"]),
                int(assessment["speed"]),
                int(assessment["keep_place"]),
                int(assessment["crowded_text"]),
                int(assessment["screen_tiredness"]),
                int(assessment["memory_after_reading"]),
                int(assessment["likes_read_aloud"]),
                int(assessment["likes_short_chunks"]),
                int(assessment["likes_calm_colours"]),
                to_int(assessment["auto_adjust_ok"]),
                int(settings["font_size"]),
                float(settings["spacing"]),
                settings["theme"],
                to_int(settings["tts_enabled"]),
                to_int(settings["voice_enabled"]),
                int(settings["tts_speed"]),
                settings["font_style"],
                settings["reading_width"],
                to_int(settings["focus_mode"]),
                settings["chunking_mode"],
                ai_mode,
                reading_profile,
                current_profile_label,
                user_id,
            ),
        )
        connection.commit()


def get_user_history_summary(user_id: int) -> dict:
    with get_connection() as connection:
        averages = connection.execute(
            """
            SELECT
                COUNT(*) AS session_count,
                AVG(COALESCE(ease, 0)) AS avg_ease,
                AVG(COALESCE(support, 0)) AS avg_support,
                AVG(COALESCE(enjoyment, 0)) AS avg_enjoyment,
                AVG(COALESCE(setup_match, 0)) AS avg_setup_match,
                AVG(COALESCE(setting_changes, 0)) AS avg_setting_changes
            FROM sessions
            WHERE user_id = ? AND completed_at IS NOT NULL
            """,
            (user_id,),
        ).fetchone()

        last_profile_row = connection.execute(
            """
            SELECT final_profile_label
            FROM sessions
            WHERE user_id = ? AND completed_at IS NOT NULL AND final_profile_label IS NOT NULL
            ORDER BY completed_at DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

    return {
        "session_count": int(averages["session_count"] or 0),
        "avg_ease": round(float(averages["avg_ease"] or 0), 2),
        "avg_support": round(float(averages["avg_support"] or 0), 2),
        "avg_enjoyment": round(float(averages["avg_enjoyment"] or 0), 2),
        "avg_setup_match": round(float(averages["avg_setup_match"] or 0), 2),
        "avg_setting_changes": round(float(averages["avg_setting_changes"] or 0), 2),
        "last_profile": last_profile_row["final_profile_label"] if last_profile_row else "none",
    }


def start_reading_session(
    user_id: int,
    book_id: str,
    recommended_profile: str,
    recommended_by_ai: bool,
    baseline_profile: str,
    assessment: dict,
    history: dict,
    settings_start: dict,
) -> int:
    created_at = utc_now()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO sessions (
                user_id,
                book_id,
                created_at,
                recommended_profile,
                recommended_by_ai,
                baseline_profile,
                difficulty,
                confidence,
                comprehension,
                speed,
                keep_place,
                crowded_text,
                screen_tiredness,
                memory_after_reading,
                likes_read_aloud,
                likes_short_chunks,
                likes_calm_colours,
                auto_adjust_ok,
                tts_enabled,
                voice_enabled,
                hist_session_count,
                hist_avg_ease,
                hist_avg_support,
                hist_avg_enjoyment,
                hist_avg_setup_match,
                hist_avg_setting_changes,
                hist_last_profile,
                font_size_start,
                spacing_start,
                theme_start,
                font_style_start,
                reading_width_start,
                focus_mode_start,
                chunking_mode_start,
                tts_speed_start
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                book_id,
                created_at,
                recommended_profile,
                to_int(recommended_by_ai),
                baseline_profile,
                assessment["difficulty"],
                int(assessment["confidence"]),
                int(assessment["comprehension"]),
                int(assessment["speed"]),
                int(assessment["keep_place"]),
                int(assessment["crowded_text"]),
                int(assessment["screen_tiredness"]),
                int(assessment["memory_after_reading"]),
                int(assessment["likes_read_aloud"]),
                int(assessment["likes_short_chunks"]),
                int(assessment["likes_calm_colours"]),
                to_int(assessment["auto_adjust_ok"]),
                to_int(assessment["tts_enabled"]),
                to_int(assessment["voice_enabled"]),
                int(history["session_count"]),
                float(history["avg_ease"]),
                float(history["avg_support"]),
                float(history["avg_enjoyment"]),
                float(history["avg_setup_match"]),
                float(history["avg_setting_changes"]),
                history["last_profile"],
                int(settings_start["font_size"]),
                float(settings_start["spacing"]),
                settings_start["theme"],
                settings_start["font_style"],
                settings_start["reading_width"],
                to_int(settings_start["focus_mode"]),
                settings_start["chunking_mode"],
                int(settings_start["tts_speed"]),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def complete_reading_session(
    session_id: int,
    final_settings: dict,
    feedback: dict,
    audio_used: bool,
    custom_tts_used: bool,
    setting_changes: int,
    final_profile_label: str,
    success_score: float,
    accepted_recommendation: bool,
):
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE sessions
            SET
                completed_at = ?,
                audio_used = ?,
                custom_tts_used = ?,
                setting_changes = ?,
                font_size_final = ?,
                spacing_final = ?,
                theme_final = ?,
                font_style_final = ?,
                reading_width_final = ?,
                focus_mode_final = ?,
                chunking_mode_final = ?,
                tts_speed_final = ?,
                ease = ?,
                support = ?,
                enjoyment = ?,
                font_comfort = ?,
                spacing_comfort = ?,
                theme_helpfulness = ?,
                voice_speed_comfort = ?,
                audio_helpfulness = ?,
                setup_match = ?,
                would_remember = ?,
                recommend = ?,
                comments = ?,
                changed_settings_reason = ?,
                final_profile_label = ?,
                success_score = ?,
                accepted_recommendation = ?
            WHERE id = ?
            """,
            (
                utc_now(),
                to_int(audio_used),
                to_int(custom_tts_used),
                int(setting_changes),
                int(final_settings["font_size"]),
                float(final_settings["spacing"]),
                final_settings["theme"],
                final_settings["font_style"],
                final_settings["reading_width"],
                to_int(final_settings["focus_mode"]),
                final_settings["chunking_mode"],
                int(final_settings["tts_speed"]),
                int(feedback["ease"]),
                int(feedback["support"]),
                int(feedback["enjoyment"]),
                int(feedback["font_comfort"]),
                int(feedback["spacing_comfort"]),
                int(feedback["theme_helpfulness"]),
                int(feedback["voice_speed_comfort"]),
                int(feedback["audio_helpfulness"]),
                int(feedback["setup_match"]),
                feedback["would_remember"],
                feedback["recommend"],
                feedback["comments"],
                feedback["changed_settings_reason"],
                final_profile_label,
                float(success_score),
                to_int(accepted_recommendation),
                session_id,
            ),
        )
        connection.commit()

def count_user_sessions(user_id: int) -> int:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT COUNT(*) AS total FROM sessions WHERE user_id = ? AND completed_at IS NOT NULL",
            (user_id,),
        ).fetchone()
    return int(row["total"] or 0)
def get_training_dataframe(min_success_score: float = 3.0) -> pd.DataFrame:
    query = """
        SELECT
            s.difficulty,
            s.confidence,
            s.comprehension,
            s.speed,
            s.keep_place,
            s.crowded_text,
            s.screen_tiredness,
            s.memory_after_reading,
            s.likes_read_aloud,
            s.likes_short_chunks,
            s.likes_calm_colours,
            s.auto_adjust_ok,
            s.tts_enabled,
            s.voice_enabled,
            s.hist_session_count,
            s.hist_avg_ease,
            s.hist_avg_support,
            s.hist_avg_enjoyment,
            s.hist_avg_setup_match,
            s.hist_avg_setting_changes,
            COALESCE(s.hist_last_profile, 'none') AS hist_last_profile,
            s.final_profile_label AS target
        FROM sessions s
        JOIN users u ON u.id = s.user_id
        WHERE
            s.completed_at IS NOT NULL
            AND s.final_profile_label IS NOT NULL
            AND s.success_score >= ?
            AND u.study_consent = 1
    """
    with get_connection() as connection:
        return pd.read_sql_query(query, connection, params=(min_success_score,))