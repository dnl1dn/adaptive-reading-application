from __future__ import annotations

from ai_profiles import PROFILE_SETTINGS, compute_success_score
from database import (
    complete_reading_session,
    create_user,
    get_user_by_username,
    get_user_history_summary,
    init_db,
    save_user_profile,
    start_reading_session,
)

DEMO_CASES = {
    "support_large_audio": {
        "assessment": {
            "difficulty": "Severe",
            "confidence": 1,
            "comprehension": 1,
            "speed": 80,
            "keep_place": 5,
            "crowded_text": 5,
            "screen_tiredness": 5,
            "memory_after_reading": 1,
            "likes_read_aloud": 5,
            "likes_short_chunks": 5,
            "likes_calm_colours": 5,
            "auto_adjust_ok": True,
            "tts_enabled": True,
            "voice_enabled": True,
        },
        "feedback": {
            "ease": 4,
            "support": 5,
            "enjoyment": 4,
            "font_comfort": 5,
            "spacing_comfort": 5,
            "theme_helpfulness": 4,
            "voice_speed_comfort": 5,
            "audio_helpfulness": 5,
            "setup_match": 5,
            "would_remember": "Yes",
            "recommend": "Yes",
            "comments": "The bigger text and extra support made this feel much easier.",
            "changed_settings_reason": "I left this mostly as it was because it already felt supportive.",
        },
    },
    "focus_high_spacing": {
        "assessment": {
            "difficulty": "Moderate",
            "confidence": 5,
            "comprehension": 5,
            "speed": 130,
            "keep_place": 5,
            "crowded_text": 5,
            "screen_tiredness": 3,
            "memory_after_reading": 3,
            "likes_read_aloud": 2,
            "likes_short_chunks": 5,
            "likes_calm_colours": 3,
            "auto_adjust_ok": True,
            "tts_enabled": True,
            "voice_enabled": False,
        },
        "feedback": {
            "ease": 4,
            "support": 4,
            "enjoyment": 4,
            "font_comfort": 4,
            "spacing_comfort": 5,
            "theme_helpfulness": 4,
            "voice_speed_comfort": 3,
            "audio_helpfulness": 3,
            "setup_match": 5,
            "would_remember": "Yes",
            "recommend": "Yes",
            "comments": "The shorter chunks and spacing helped me keep my place better.",
            "changed_settings_reason": "I did not need to change much because the spacing already helped.",
        },
    },
    "balanced_default": {
        "assessment": {
            "difficulty": "Mild",
            "confidence": 8,
            "comprehension": 8,
            "speed": 190,
            "keep_place": 2,
            "crowded_text": 2,
            "screen_tiredness": 2,
            "memory_after_reading": 4,
            "likes_read_aloud": 2,
            "likes_short_chunks": 2,
            "likes_calm_colours": 2,
            "auto_adjust_ok": True,
            "tts_enabled": True,
            "voice_enabled": False,
        },
        "feedback": {
            "ease": 4,
            "support": 4,
            "enjoyment": 4,
            "font_comfort": 4,
            "spacing_comfort": 4,
            "theme_helpfulness": 3,
            "voice_speed_comfort": 3,
            "audio_helpfulness": 2,
            "setup_match": 5,
            "would_remember": "Yes",
            "recommend": "Yes",
            "comments": "This felt clear without being too heavy.",
            "changed_settings_reason": "I barely changed anything because the setup already felt fine.",
        },
    },
    "calm_low_stimulation": {
        "assessment": {
            "difficulty": "Moderate",
            "confidence": 5,
            "comprehension": 5,
            "speed": 120,
            "keep_place": 3,
            "crowded_text": 3,
            "screen_tiredness": 5,
            "memory_after_reading": 3,
            "likes_read_aloud": 2,
            "likes_short_chunks": 3,
            "likes_calm_colours": 5,
            "auto_adjust_ok": True,
            "tts_enabled": True,
            "voice_enabled": False,
        },
        "feedback": {
            "ease": 4,
            "support": 4,
            "enjoyment": 4,
            "font_comfort": 4,
            "spacing_comfort": 4,
            "theme_helpfulness": 5,
            "voice_speed_comfort": 3,
            "audio_helpfulness": 3,
            "setup_match": 5,
            "would_remember": "Yes",
            "recommend": "Yes",
            "comments": "The calmer colours made the screen feel easier on my eyes.",
            "changed_settings_reason": "I kept this mostly the same because the softer look helped.",
        },
    },
    "independent_wide": {
        "assessment": {
            "difficulty": "Mild",
            "confidence": 10,
            "comprehension": 10,
            "speed": 240,
            "keep_place": 1,
            "crowded_text": 1,
            "screen_tiredness": 1,
            "memory_after_reading": 5,
            "likes_read_aloud": 1,
            "likes_short_chunks": 1,
            "likes_calm_colours": 1,
            "auto_adjust_ok": True,
            "tts_enabled": False,
            "voice_enabled": False,
        },
        "feedback": {
            "ease": 5,
            "support": 3,
            "enjoyment": 4,
            "font_comfort": 4,
            "spacing_comfort": 4,
            "theme_helpfulness": 3,
            "voice_speed_comfort": 3,
            "audio_helpfulness": 1,
            "setup_match": 5,
            "would_remember": "Yes",
            "recommend": "Yes",
            "comments": "This felt simple and easy without extra help getting in the way.",
            "changed_settings_reason": "I did not need any real changes here.",
        },
    },
    "audio_guided": {
        "assessment": {
            "difficulty": "Severe",
            "confidence": 2,
            "comprehension": 2,
            "speed": 90,
            "keep_place": 5,
            "crowded_text": 5,
            "screen_tiredness": 4,
            "memory_after_reading": 2,
            "likes_read_aloud": 5,
            "likes_short_chunks": 5,
            "likes_calm_colours": 4,
            "auto_adjust_ok": True,
            "tts_enabled": True,
            "voice_enabled": True,
        },
        "feedback": {
            "ease": 4,
            "support": 5,
            "enjoyment": 4,
            "font_comfort": 4,
            "spacing_comfort": 4,
            "theme_helpfulness": 4,
            "voice_speed_comfort": 5,
            "audio_helpfulness": 5,
            "setup_match": 5,
            "would_remember": "Yes",
            "recommend": "Yes",
            "comments": "The audio and chunking made this much easier to follow.",
            "changed_settings_reason": "I kept the audio support because that helped the most.",
        },
    },
    "memory_support": {
        "assessment": {
            "difficulty": "Moderate",
            "confidence": 4,
            "comprehension": 4,
            "speed": 120,
            "keep_place": 3,
            "crowded_text": 3,
            "screen_tiredness": 3,
            "memory_after_reading": 1,
            "likes_read_aloud": 3,
            "likes_short_chunks": 5,
            "likes_calm_colours": 3,
            "auto_adjust_ok": True,
            "tts_enabled": True,
            "voice_enabled": False,
        },
        "feedback": {
            "ease": 4,
            "support": 4,
            "enjoyment": 4,
            "font_comfort": 4,
            "spacing_comfort": 5,
            "theme_helpfulness": 4,
            "voice_speed_comfort": 4,
            "audio_helpfulness": 4,
            "setup_match": 5,
            "would_remember": "Yes",
            "recommend": "Yes",
            "comments": "The chunked layout helped me remember what I had just read.",
            "changed_settings_reason": "I kept the shorter chunks because they helped the most.",
        },
    },
    "fatigue_relief": {
        "assessment": {
            "difficulty": "Moderate",
            "confidence": 5,
            "comprehension": 5,
            "speed": 115,
            "keep_place": 3,
            "crowded_text": 3,
            "screen_tiredness": 5,
            "memory_after_reading": 3,
            "likes_read_aloud": 2,
            "likes_short_chunks": 3,
            "likes_calm_colours": 5,
            "auto_adjust_ok": True,
            "tts_enabled": True,
            "voice_enabled": False,
        },
        "feedback": {
            "ease": 4,
            "support": 4,
            "enjoyment": 4,
            "font_comfort": 4,
            "spacing_comfort": 4,
            "theme_helpfulness": 5,
            "voice_speed_comfort": 3,
            "audio_helpfulness": 3,
            "setup_match": 5,
            "would_remember": "Yes",
            "recommend": "Yes",
            "comments": "The softer colours made the screen feel easier and less tiring.",
            "changed_settings_reason": "I mostly left it alone because it already felt calmer on my eyes.",
        },
    },
    "high_contrast_focus": {
        "assessment": {
            "difficulty": "Moderate",
            "confidence": 5,
            "comprehension": 5,
            "speed": 135,
            "keep_place": 5,
            "crowded_text": 5,
            "screen_tiredness": 3,
            "memory_after_reading": 3,
            "likes_read_aloud": 2,
            "likes_short_chunks": 5,
            "likes_calm_colours": 1,
            "auto_adjust_ok": True,
            "tts_enabled": False,
            "voice_enabled": False,
        },
        "feedback": {
            "ease": 4,
            "support": 4,
            "enjoyment": 3,
            "font_comfort": 4,
            "spacing_comfort": 5,
            "theme_helpfulness": 5,
            "voice_speed_comfort": 3,
            "audio_helpfulness": 1,
            "setup_match": 5,
            "would_remember": "Yes",
            "recommend": "Yes",
            "comments": "The stronger contrast and focus made it easier to track the text.",
            "changed_settings_reason": "I kept the contrast because it made the words stand out more.",
        },
    },
    "light_audio_support": {
        "assessment": {
            "difficulty": "Mild",
            "confidence": 7,
            "comprehension": 7,
            "speed": 150,
            "keep_place": 2,
            "crowded_text": 2,
            "screen_tiredness": 2,
            "memory_after_reading": 4,
            "likes_read_aloud": 5,
            "likes_short_chunks": 2,
            "likes_calm_colours": 2,
            "auto_adjust_ok": True,
            "tts_enabled": True,
            "voice_enabled": False,
        },
        "feedback": {
            "ease": 4,
            "support": 4,
            "enjoyment": 4,
            "font_comfort": 4,
            "spacing_comfort": 4,
            "theme_helpfulness": 3,
            "voice_speed_comfort": 4,
            "audio_helpfulness": 4,
            "setup_match": 5,
            "would_remember": "Yes",
            "recommend": "Yes",
            "comments": "Having some audio there helped without making the whole setup feel too heavy.",
            "changed_settings_reason": "I liked having the audio there but did not need a lot of other support.",
        },
    },
}


def build_settings_for_profile(profile_label: str) -> dict:
    profile = PROFILE_SETTINGS[profile_label]
    return {
        "font_size": profile["font_size"],
        "spacing": profile["spacing"],
        "theme": profile["theme"],
        "tts_enabled": profile["tts_enabled"],
        "voice_enabled": profile["voice_enabled"],
        "tts_speed": profile["tts_speed"],
        "font_style": profile["font_style"],
        "reading_width": profile["reading_width"],
        "focus_mode": profile["focus_mode"],
        "chunking_mode": profile["chunking_mode"],
    }


def seed_profile(profile_label: str, how_many: int = 3):
    case = DEMO_CASES[profile_label]
    assessment = case["assessment"]
    final_settings = build_settings_for_profile(profile_label)
    feedback = case["feedback"]
    success_score = compute_success_score(feedback)

    for index in range(1, how_many + 1):
        username = f"seed_{profile_label}_{index}"

        if get_user_by_username(username):
            print(f"Skipping existing user: {username}")
            continue

        # I kept these names predictable so it is easy to see what got generated.
        user = create_user(username, True)

        save_user_profile(
            user_id=user["id"],
            assessment=assessment,
            settings=final_settings,
            ai_mode="Balanced Support",
            reading_profile="Demo Reader",
            current_profile_label=profile_label,
        )

        history = get_user_history_summary(user["id"])

        session_id = start_reading_session(
            user_id=user["id"],
            book_id="alice-gutenberg",
            recommended_profile=profile_label,
            recommended_by_ai=True,
            baseline_profile=profile_label,
            assessment=assessment,
            history=history,
            settings_start=final_settings,
        )

        complete_reading_session(
            session_id=session_id,
            final_settings=final_settings,
            feedback=feedback,
            audio_used=bool(final_settings["tts_enabled"]),
            custom_tts_used=False,
            setting_changes=0,
            final_profile_label=profile_label,
            success_score=success_score,
            accepted_recommendation=True,
        )

        print(f"Created seeded session for: {username} -> {profile_label}")


def main():
    init_db()

    for profile_label in DEMO_CASES:
        seed_profile(profile_label, how_many=3)

    print("\nDone. Seeded demo sessions for all 10 profiles.")


if __name__ == "__main__":
    main()