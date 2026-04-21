import streamlit as st

from ai_profiles import profile_title
from ai_recommender import get_model_details, model_is_available
from app_state import init_session_state
from database import count_user_sessions, get_user_history_summary, init_db
from profile_logic import ai_explanation
from styles import apply_global_styles
from ui_helpers import render_nav_buttons, render_progress

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

init_db()
init_session_state()
apply_global_styles()
render_progress(5, "Dashboard")

if not st.session_state["current_user_id"]:
    st.warning("Please sign in or create a profile first.")
    if st.button("Go to Sign In", type="primary"):
        st.switch_page("main.py")
    st.stop()

history = get_user_history_summary(st.session_state["current_user_id"])
session_count = count_user_sessions(st.session_state["current_user_id"])
model_info = get_model_details()

st.markdown(
    f"""
    <div class="hero-box" style="padding:2rem;">
        <div class="hero-title" style="font-size:2.2rem;">📊 {st.session_state["current_username"]}'s reading dashboard</div>
        <div class="hero-subtitle">
            This brings together the current setup, saved profile, usage, and feedback in one place.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

summary_cards = [
    ("Ease of reading", st.session_state["ease"]),
    ("Helpfulness", st.session_state["support"]),
    ("Enjoyment", st.session_state["enjoyment"]),
]

summary_cols = st.columns(3)
for col, (label, value) in zip(summary_cols, summary_cards):
    with col:
        st.markdown(
            f"""
            <div class="result-card">
                <p style="color:#444;">{label}</p>
                <div class="big-number">{value}/5</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")
left, right = st.columns(2, gap="large")

with left:
    st.markdown(
        f"""
        <div class="result-card">
            <h3 style="margin-top:0; color:#1e1e2f;">Saved profile and usage</h3>
            <p style="color:#444;"><b>Saved profile:</b> {profile_title(st.session_state["current_profile_label"])}</p>
            <p style="color:#444;"><b>Completed sessions:</b> {session_count}</p>
            <p style="color:#444;"><b>Average ease:</b> {history["avg_ease"]}</p>
            <p style="color:#444;"><b>Average support:</b> {history["avg_support"]}</p>
            <p style="color:#444;"><b>Average enjoyment:</b> {history["avg_enjoyment"]}</p>
            <p style="color:#444;"><b>Average setup match:</b> {history["avg_setup_match"]}</p>
            <p style="color:#444;"><b>Average setting changes:</b> {history["avg_setting_changes"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    model_name = model_info["model_name"] if model_info else "No trained model yet"
    trained_at = model_info["trained_at"] if model_info else "Not trained yet"

    st.markdown(
        f"""
        <div class="result-card">
            <h3 style="margin-top:0; color:#1e1e2f;">AI recommender</h3>
            <p style="color:#444;"><b>Model available:</b> {"Yes" if model_is_available() else "No"}</p>
            <p style="color:#444;"><b>Model name:</b> {model_name}</p>
            <p style="color:#444;"><b>Last trained:</b> {trained_at}</p>
            <p style="color:#444;"><b>Last recommendation source:</b> {st.session_state["ai_recommendation_source"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
st.markdown('<div class="section-title">📊 Support Summary</div>', unsafe_allow_html=True)
st.info(ai_explanation(st.session_state["ai_mode"]))

st.write("")
st.markdown(
    f"""
    <div class="result-card">
        <h3 style="margin-top:0; color:#1e1e2f;">Extra comments</h3>
        <p style="color:#444;"><b>Reason for changing settings:</b> {st.session_state["changed_settings_reason"] if st.session_state["changed_settings_reason"] else "No reason added."}</p>
        <p style="color:#444;"><b>General comments:</b> {st.session_state["comments"] if st.session_state["comments"] else "No comments submitted."}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
render_nav_buttons([
    ("🏠 Sign In", "main.py"),
    ("📚 Books", "pages/Bookshelf.py"),
    ("📖 Reading Space", "pages/BookViewer.py"),
])