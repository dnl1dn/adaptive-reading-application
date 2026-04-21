import streamlit as st

from ai_profiles import apply_profile_to_state, profile_description, profile_title
from ai_recommender import recommend_profile
from app_state import (
    assessment_snapshot_from_state,
    init_session_state,
    settings_snapshot_from_state,
)
from database import get_user_history_summary, init_db, save_user_profile
from profile_logic import baseline_profile_from_assessment, compute_support_profile
from styles import apply_global_styles
from ui_helpers import render_nav_buttons, render_progress, render_question_row

st.set_page_config(page_title="My Setup", page_icon="🧠", layout="wide")

init_db()
init_session_state()
apply_global_styles()
render_progress(1, "My Reading Setup")

if not st.session_state["current_user_id"]:
    st.warning("Please sign in or create a profile first.")
    if st.button("Go to Sign In", type="primary"):
        st.switch_page("main.py")
    st.stop()

st.markdown(
    """
    <div class="hero-box" style="padding:2.2rem;">
        <div class="hero-title" style="font-size:2.4rem;">🧠 Let’s set up your reading space</div>
        <div class="hero-subtitle">
            These questions help the app work out what sort of reading support feels best for you.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
left, right = st.columns([1.2, 0.8], gap="large")

with left:
    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🛠 Reading Check-In</div>', unsafe_allow_html=True)
    st.caption("Try to answer honestly. There is no right or wrong answer here.")

    render_question_row("How much help would you like while reading?", "assess_q1")
    difficulty = st.selectbox(
        "",
        ["Mild", "Moderate", "Severe"],
        index=["Mild", "Moderate", "Severe"].index(st.session_state["difficulty"]),
        key="difficulty_select",
    )

    render_question_row("How easy is it for you to read on a screen?", "assess_q2")
    confidence = st.slider("", 1, 10, int(st.session_state["confidence"]), key="confidence_slider")

    render_question_row("How easy is it to understand what you read?", "assess_q3")
    comprehension = st.slider("", 1, 10, int(st.session_state["comprehension"]), key="comprehension_slider")

    render_question_row("How quickly do you usually like to read?", "assess_q4")
    speed = st.slider("", 50, 300, int(st.session_state["speed"]), key="speed_slider")

    st.write("")
    st.markdown('<div class="section-title">👀 What reading feels like</div>', unsafe_allow_html=True)

    render_question_row("How hard is it to keep your place when you read?", "assess_q5")
    keep_place = st.slider("", 1, 5, int(st.session_state["keep_place"]), key="keep_place_slider")

    render_question_row("Do the words ever feel too squashed or busy on the screen?", "assess_q6")
    crowded_text = st.slider("", 1, 5, int(st.session_state["crowded_text"]), key="crowded_text_slider")

    render_question_row("Do your eyes or head get tired when you read on a screen?", "assess_q7")
    screen_tiredness = st.slider("", 1, 5, int(st.session_state["screen_tiredness"]), key="screen_tiredness_slider")

    render_question_row("After one page, how much do you usually remember?", "assess_q8")
    memory_after_reading = st.slider("", 1, 5, int(st.session_state["memory_after_reading"]), key="memory_after_slider")

    render_question_row("Would it help if the words were read out loud too?", "assess_q9")
    likes_read_aloud = st.slider("", 1, 5, int(st.session_state["likes_read_aloud"]), key="likes_read_aloud_slider")

    render_question_row("Do shorter chunks of text help?", "assess_q10")
    likes_short_chunks = st.slider("", 1, 5, int(st.session_state["likes_short_chunks"]), key="likes_short_chunks_slider")

    render_question_row("Do calmer colours help you read better?", "assess_q11")
    likes_calm_colours = st.slider("", 1, 5, int(st.session_state["likes_calm_colours"]), key="likes_calm_colours_slider")

    st.write("")
    st.markdown('<div class="section-title">🎧 Accessibility Options</div>', unsafe_allow_html=True)

    render_question_row("Would you like audio support available while reading?", "assess_q12")
    tts_enabled = st.checkbox("Keep audio support available", value=st.session_state["tts_enabled"])

    render_question_row("Would you like voice input available as a support tool?", "assess_q13")
    voice_enabled = st.checkbox("Keep voice input available", value=st.session_state["voice_enabled"])

    render_question_row("Is it okay if the app learns from your feedback and changes your setup next time?", "assess_q14")
    auto_adjust_ok = st.checkbox("Yes, the app can keep learning from what worked for me", value=st.session_state["auto_adjust_ok"])

    st.write("")
    if st.button("Save My Setup", use_container_width=True, type="primary"):
        st.session_state["difficulty"] = difficulty
        st.session_state["confidence"] = confidence
        st.session_state["comprehension"] = comprehension
        st.session_state["speed"] = speed
        st.session_state["keep_place"] = keep_place
        st.session_state["crowded_text"] = crowded_text
        st.session_state["screen_tiredness"] = screen_tiredness
        st.session_state["memory_after_reading"] = memory_after_reading
        st.session_state["likes_read_aloud"] = likes_read_aloud
        st.session_state["likes_short_chunks"] = likes_short_chunks
        st.session_state["likes_calm_colours"] = likes_calm_colours
        st.session_state["tts_enabled"] = tts_enabled
        st.session_state["voice_enabled"] = voice_enabled
        st.session_state["auto_adjust_ok"] = auto_adjust_ok

        ai_mode, reading_profile = compute_support_profile(difficulty, comprehension, confidence)
        st.session_state["ai_mode"] = ai_mode
        st.session_state["reading_profile"] = reading_profile
        st.session_state["assessment_completed"] = True

        baseline_profile = baseline_profile_from_assessment(
            difficulty=difficulty,
            confidence=confidence,
            comprehension=comprehension,
            speed=speed,
            keep_place=keep_place,
            crowded_text=crowded_text,
            screen_tiredness=screen_tiredness,
            likes_read_aloud=likes_read_aloud,
            likes_short_chunks=likes_short_chunks,
            likes_calm_colours=likes_calm_colours,
            tts_enabled=tts_enabled,
            voice_enabled=voice_enabled,
        )

        history = get_user_history_summary(st.session_state["current_user_id"])
        recommendation = recommend_profile(
            assessment=assessment_snapshot_from_state(),
            history=history,
            fallback_profile=baseline_profile,
        )

        st.session_state["ai_recommended_profile"] = recommendation["profile"]
        st.session_state["ai_recommendation_source"] = recommendation["source"]
        st.session_state["ai_model_name"] = recommendation["model_name"]

        apply_profile_to_state(recommendation["profile"], st.session_state)

        st.session_state["selected_shelf"] = {
            "Extra Support": "Calm Reads",
            "Balanced Support": "Recommended",
        }.get(ai_mode, "Adventure Shelf")

        save_user_profile(
            user_id=st.session_state["current_user_id"],
            assessment=assessment_snapshot_from_state(),
            settings=settings_snapshot_from_state(),
            ai_mode=ai_mode,
            reading_profile=reading_profile,
            current_profile_label=st.session_state["current_profile_label"],
        )

        st.success(f'The app assigned the "{profile_title(recommendation["profile"])}" profile.')
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    recommended_label = st.session_state.get("ai_recommended_profile", "balanced_default")
    source = st.session_state.get("ai_recommendation_source", "baseline rules")

    st.markdown(
        f"""
        <div class="soft-card">
            <h3 style="margin-top:0; color:#1e1e2f;">🤖 Recommended profile</h3>
            <p style="color:#444;"><b>Profile:</b> {profile_title(recommended_label)}</p>
            <p style="color:#444;">{profile_description(recommended_label)}</p>
            <p style="color:#444;"><b>Source:</b> {source}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="soft-card" style="margin-top:1rem;">
            <h3 style="margin-top:0; color:#1e1e2f;">Current support mode</h3>
            <p style="color:#444;"><b>AI mode:</b> {st.session_state["ai_mode"]}</p>
            <p style="color:#444;"><b>Reading profile:</b> {st.session_state["reading_profile"]}</p>
            <p style="color:#444;"><b>Suggested shelf:</b> {st.session_state["selected_shelf"]}</p>
            <p style="color:#444;"><b>Auto adjust:</b> {"On" if st.session_state["auto_adjust_ok"] else "Off"}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
render_nav_buttons([
    ("🏠 Back to Sign In", "main.py"),
    ("📚 Go to Books", "pages/Bookshelf.py"),
    ("📊 Dashboard", "pages/Dashboard.py"),
])