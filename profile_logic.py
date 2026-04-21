def compute_support_profile(difficulty, comprehension, confidence):
    if difficulty == "Severe" or comprehension <= 4 or confidence <= 4:
        return "Extra Support", "Supportive Reader"
    if difficulty == "Moderate" or comprehension <= 7 or confidence <= 7:
        return "Balanced Support", "Balanced Reader"
    return "Independent Mode", "Independent Reader"


def baseline_profile_from_assessment(
    difficulty: str,
    confidence: int,
    comprehension: int,
    speed: int,
    keep_place: int,
    crowded_text: int,
    screen_tiredness: int,
    likes_read_aloud: int,
    likes_short_chunks: int,
    likes_calm_colours: int,
    tts_enabled: bool,
    voice_enabled: bool,
) -> str:
    # I added a few more profile routes here so the fallback logic still makes sense even without the trained model.
    if difficulty == "Severe" and confidence <= 2 and comprehension <= 2:
        if likes_read_aloud >= 5 and voice_enabled:
            return "support_large_audio"

    if likes_read_aloud >= 5 and (voice_enabled or tts_enabled) and speed <= 110:
        return "audio_guided"

    if crowded_text >= 5 and keep_place >= 5 and likes_calm_colours <= 2 and likes_read_aloud <= 3:
        return "high_contrast_focus"

    if memory_after_score(comprehension, keep_place=None):
        pass

    if screen_tiredness >= 5 and likes_calm_colours >= 4:
        return "fatigue_relief"

    if comprehension <= 5 and likes_short_chunks >= 4 and likes_read_aloud >= 3:
        return "memory_support"

    if likes_read_aloud >= 4 and difficulty != "Severe" and comprehension >= 5:
        return "light_audio_support"

    if crowded_text >= 4 or keep_place >= 4 or likes_short_chunks >= 4:
        return "focus_high_spacing"

    if screen_tiredness >= 4 or likes_calm_colours >= 4:
        return "calm_low_stimulation"

    if difficulty == "Mild" and confidence >= 8 and comprehension >= 8 and speed >= 190:
        return "independent_wide"

    return "balanced_default"


def memory_after_score(comprehension: int, keep_place):
    return comprehension <= 5


def ai_explanation(ai_mode: str):
    if ai_mode == "Extra Support":
        return "The app is giving more support here, so the text is calmer, clearer, and easier to manage."
    if ai_mode == "Balanced Support":
        return "The app is aiming for a middle ground, keeping reading comfortable without changing too much at once."
    return "The app is keeping things lighter here, so reading stays natural while still feeling clear and comfortable."


def get_theme_palette(theme_name: str):
    palettes = {
        "Bright": {"bg": "#FFFDF2", "text": "#1E1E2F"},
        "Soft Pastel": {"bg": "#F9F3FF", "text": "#2E2440"},
        "High Contrast": {"bg": "#111111", "text": "#FFFFFF"},
        "Cool Blue": {"bg": "#EEF7FF", "text": "#13304A"},
        "Warm Pink": {"bg": "#FFF1F7", "text": "#4B1F35"},
    }
    return palettes.get(theme_name, palettes["Bright"])