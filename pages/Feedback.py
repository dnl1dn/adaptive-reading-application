import streamlit as st

from ai_profiles import closest_profile_from_settings, compute_success_score, profile_title
from app_state import (
    assessment_snapshot_from_state,
    feedback_snapshot_from_state,
    init_session_state,
    settings_snapshot_from_state,
)
from database import complete_reading_session, init_db, save_user_profile
from styles import apply_global_styles
from ui_helpers import render_nav_buttons, render_progress, render_question_row

st.set_page_config(page_title="Feedback", page_icon="📝", layout="wide")

init_db()
init_session_state()
apply_global_styles()
render_progress(4, "Feedback")

if not st.session_state["current_user_id"]:
    st.warning("Please sign in or create a profile first.")
    if st.button("Go to Sign In", type="primary"):
        st.switch_page("main.py")
    st.stop()

st.markdown(
    """
    <div class="hero-box" style="padding:2rem;">
        <div class="hero-title" style="font-size:2.2rem;">📝 Tell us how it felt</div>
        <div class="hero-subtitle">
            This is the bit that helps the app learn what actually worked and what should change next time.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
left, right = st.columns([1.1, 0.9], gap="large")

with left:
    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💬 Reading Feedback</div>', unsafe_allow_html=True)

    feedback_slider_questions = [
        ("How easy was the reading experience overall?", "fb_q1", "ease"),
        ("How helpful was the reading support?", "fb_q2", "support"),
        ("How enjoyable was the reading experience?", "fb_q3", "enjoyment"),
        ("How comfortable was the text size?", "fb_q4", "font_comfort"),
        ("How comfortable was the spacing between lines?", "fb_q5", "spacing_comfort"),
        ("How helpful was the colour style?", "fb_q6", "theme_helpfulness"),
        ("How comfortable was the voice speed?", "fb_q7", "voice_speed_comfort"),
        ("How helpful was the audio support?", "fb_q8", "audio_helpfulness"),
        ("How well did the setup match what you needed?", "fb_q9", "setup_match"),
    ]

    slider_values = {}
    for question, key, state_key in feedback_slider_questions:
        render_question_row(question, key)
        default_value = int(st.session_state[state_key]) if st.session_state[state_key] else 3
        slider_values[state_key] = st.slider("", 1, 5, default_value, key=f"{state_key}_slider")

    render_question_row("Would you want the app to remember your preferred settings next time?", "fb_q10")
    would_remember = st.radio(
        "",
        ["Yes", "Maybe", "No"],
        horizontal=True,
        index=["Yes", "Maybe", "No"].index(st.session_state["would_remember"]) if st.session_state["would_remember"] in ["Yes", "Maybe", "No"] else 2,
        key="fb_would_remember",
    )

    render_question_row("Would you want to use this again?", "fb_q11")
    recommend = st.radio(
        "",
        ["Yes", "Maybe", "No"],
        horizontal=True,
        index=["Yes", "Maybe", "No"].index(st.session_state["recommend"]) if st.session_state["recommend"] in ["Yes", "Maybe", "No"] else 2,
        key="fb_recommend",
    )

    render_question_row("If you changed any settings, what made you change them?", "fb_q12")
    changed_settings_reason = st.text_area(
        "",
        value=st.session_state["changed_settings_reason"],
        placeholder="You can explain what did not feel right at first.",
        key="fb_changed_reason",
    )

    render_question_row("Anything else you want to say?", "fb_q13")
    comments = st.text_area(
        "",
        value=st.session_state["comments"],
        placeholder="Write what worked well or what should improve.",
        key="fb_comments",
    )

    render_question_row("Should the app keep learning from what worked today?", "fb_q14")
    auto_adjust_ok = st.checkbox(
        "Yes, keep the good changes for next time",
        value=st.session_state["auto_adjust_ok"],
        key="fb_auto_adjust_ok",
    )

    render_question_row("If needed, you can also adjust the voice speed here.", "fb_q15")
    tts_speed = st.slider("", 100, 220, int(st.session_state["tts_speed"]), key="fb_tts_speed")

    st.write("")
    if st.button("Submit Feedback", use_container_width=True, type="primary"):
        st.session_state.update(slider_values)
        st.session_state["would_remember"] = would_remember
        st.session_state["recommend"] = recommend
        st.session_state["changed_settings_reason"] = changed_settings_reason
        st.session_state["comments"] = comments
        st.session_state["tts_speed"] = tts_speed
        st.session_state["auto_adjust_ok"] = auto_adjust_ok

        final_settings = settings_snapshot_from_state()
        final_profile_label = closest_profile_from_settings(final_settings)
        feedback = feedback_snapshot_from_state()
        success_score = compute_success_score(feedback)
        accepted_recommendation = final_profile_label == st.session_state.get("ai_recommended_profile")

        if st.session_state.get("active_session_id"):
            complete_reading_session(
                session_id=int(st.session_state["active_session_id"]),
                final_settings=final_settings,
                feedback=feedback,
                audio_used=bool(st.session_state["audio_used"]),
                custom_tts_used=bool(st.session_state["custom_tts_used"]),
                setting_changes=int(st.session_state["setting_changes"]),
                final_profile_label=final_profile_label,
                success_score=success_score,
                accepted_recommendation=accepted_recommendation,
            )

        # I only push the final setup back into the saved profile when the user is okay with that.
        if auto_adjust_ok:
            st.session_state["current_profile_label"] = final_profile_label
            save_user_profile(
                user_id=st.session_state["current_user_id"],
                assessment=assessment_snapshot_from_state(),
                settings=final_settings,
                ai_mode=st.session_state["ai_mode"],
                reading_profile=st.session_state["reading_profile"],
                current_profile_label=final_profile_label,
            )

        st.session_state["active_session_id"] = None
        st.session_state["active_book_id"] = None

        st.success("Feedback saved. The app will use this in later recommendations.")
        st.balloons()

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown(
        f"""
        <div class="soft-card">
            <h3 style="margin-top:0; color:#1e1e2f;">Current saved profile</h3>
            <p style="color:#444;"><b>{profile_title(st.session_state["current_profile_label"])}</b></p>
            <p style="color:#444;">Auto adjust is <b>{"on" if st.session_state["auto_adjust_ok"] else "off"}</b>.</p>
            <p style="color:#444;">If it is on, the app saves the final setup that worked and uses it next time.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="soft-card" style="margin-top:1rem;">
            <h3 style="margin-top:0; color:#1e1e2f;">What the AI uses</h3>
            <p style="color:#444;">The model looks at the setup answers, session history, and feedback from finished sessions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
render_nav_buttons([
    ("📖 Reading Space", "pages/BookViewer.py"),
    ("📚 Books", "pages/Bookshelf.py"),
    ("📊 Dashboard", "pages/Dashboard.py"),
])