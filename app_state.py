import streamlit as st

SETTING_KEYS = [
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
]

ASSESSMENT_KEYS = [
    "difficulty",
    "confidence",
    "comprehension",
    "speed",
    "tts_enabled",
    "voice_enabled",
    "keep_place",
    "crowded_text",
    "screen_tiredness",
    "memory_after_reading",
    "likes_read_aloud",
    "likes_short_chunks",
    "likes_calm_colours",
    "auto_adjust_ok",
]

FEEDBACK_KEYS = [
    "ease",
    "support",
    "enjoyment",
    "font_comfort",
    "spacing_comfort",
    "theme_helpfulness",
    "voice_speed_comfort",
    "audio_helpfulness",
    "setup_match",
    "would_remember",
    "recommend",
    "comments",
    "changed_settings_reason",
]

DEFAULT_STATE = {
    "difficulty": "Moderate",
    "font_size": 22,
    "spacing": 1.6,
    "theme": "Bright",
    "tts_enabled": True,
    "voice_enabled": False,
    "confidence": 5,
    "speed": 140,
    "comprehension": 5,
    "keep_place": 3,
    "crowded_text": 3,
    "screen_tiredness": 3,
    "memory_after_reading": 3,
    "likes_read_aloud": 3,
    "likes_short_chunks": 3,
    "likes_calm_colours": 3,
    "auto_adjust_ok": True,
    "ai_mode": "Balanced Support",
    "reading_profile": "Balanced Reader",
    "selected_book": None,
    "selected_shelf": "Recommended",
    "audio_used": False,
    "custom_tts_used": False,
    "setting_changes": 0,
    "ease": 0,
    "support": 0,
    "enjoyment": 0,
    "recommend": "No response",
    "comments": "",
    "voice_query": "",
    "voice_book_text": "",
    "book_custom_tts_text": "",
    "tts_speed": 165,
    "font_style": "Simple",
    "reading_width": "Normal",
    "focus_mode": False,
    "chunking_mode": "Full Text",
    "font_comfort": 0,
    "spacing_comfort": 0,
    "theme_helpfulness": 0,
    "voice_speed_comfort": 0,
    "audio_helpfulness": 0,
    "setup_match": 0,
    "would_remember": "No response",
    "changed_settings_reason": "",
    "current_user_id": None,
    "current_username": "",
    "study_consent": False,
    "assessment_completed": False,
    "current_profile_label": "balanced_default",
    "ai_recommended_profile": "balanced_default",
    "ai_recommendation_source": "baseline rules",
    "ai_model_name": "None",
    "active_session_id": None,
    "active_book_id": None,
}


def init_session_state():
    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_current_user():
    # I reset this here so one profile does not mess up another one.
    for key, value in DEFAULT_STATE.items():
        st.session_state[key] = value


def settings_snapshot_from_state():
    return {key: st.session_state.get(key) for key in SETTING_KEYS}


def assessment_snapshot_from_state():
    return {key: st.session_state.get(key) for key in ASSESSMENT_KEYS}


def feedback_snapshot_from_state():
    return {key: st.session_state.get(key) for key in FEEDBACK_KEYS}


def load_user_record_into_session(user: dict):
    clear_current_user()

    st.session_state["current_user_id"] = user["id"]
    st.session_state["current_username"] = user["username"]
    st.session_state["study_consent"] = bool(user["study_consent"])
    st.session_state["assessment_completed"] = bool(user["assessment_completed"])

    st.session_state["difficulty"] = user["difficulty"]
    st.session_state["confidence"] = int(user["confidence"])
    st.session_state["comprehension"] = int(user["comprehension"])
    st.session_state["speed"] = int(user["speed"])
    st.session_state["keep_place"] = int(user["keep_place"])
    st.session_state["crowded_text"] = int(user["crowded_text"])
    st.session_state["screen_tiredness"] = int(user["screen_tiredness"])
    st.session_state["memory_after_reading"] = int(user["memory_after_reading"])
    st.session_state["likes_read_aloud"] = int(user["likes_read_aloud"])
    st.session_state["likes_short_chunks"] = int(user["likes_short_chunks"])
    st.session_state["likes_calm_colours"] = int(user["likes_calm_colours"])
    st.session_state["auto_adjust_ok"] = bool(user["auto_adjust_ok"])

    st.session_state["font_size"] = int(user["font_size"])
    st.session_state["spacing"] = float(user["spacing"])
    st.session_state["theme"] = user["theme"]
    st.session_state["tts_enabled"] = bool(user["tts_enabled"])
    st.session_state["voice_enabled"] = bool(user["voice_enabled"])
    st.session_state["tts_speed"] = int(user["tts_speed"])
    st.session_state["font_style"] = user["font_style"]
    st.session_state["reading_width"] = user["reading_width"]
    st.session_state["focus_mode"] = bool(user["focus_mode"])
    st.session_state["chunking_mode"] = user["chunking_mode"]

    st.session_state["ai_mode"] = user["ai_mode"]
    st.session_state["reading_profile"] = user["reading_profile"]
    st.session_state["current_profile_label"] = user["current_profile_label"]
    st.session_state["ai_recommended_profile"] = user["current_profile_label"]
    st.session_state["ai_recommendation_source"] = "saved profile"