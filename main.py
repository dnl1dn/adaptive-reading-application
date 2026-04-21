import re

import streamlit as st

from ai_recommender import get_model_details, model_is_available
from app_state import clear_current_user, init_session_state, load_user_record_into_session
from database import create_user, get_user_by_username, init_db, list_users, update_last_login
from styles import apply_global_styles

st.set_page_config(
    page_title="BrightPath Reading",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()
init_session_state()
apply_global_styles()

st.markdown("## 📘 BrightPath Reading")

if st.session_state["current_user_id"]:
    left, right = st.columns([1.2, 1], gap="large")

    with left:
        st.markdown(
            f"""
            <div class="hero-box">
                <div class="hero-title">Welcome back, {st.session_state["current_username"]}</div>
                <div class="hero-subtitle">
                    Your saved reading profile is ready to go. You can carry on reading,
                    review your setup, or switch to another profile.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        model_info = get_model_details()
        model_name = model_info["model_name"] if model_info else "No trained model yet"

        st.markdown(
            f"""
            <div class="soft-card" style="min-height:260px;">
                <h3 style="margin-top:0; color:#1e1e2f;">🤖 Personalisation status</h3>
                <p style="color:#444;"><b>Current saved profile:</b> {st.session_state.get("current_profile_label", "balanced_default").replace("_", " ").title()}</p>
                <p style="color:#444;"><b>AI model ready:</b> {"Yes" if model_is_available() else "No"}</p>
                <p style="color:#444;"><b>Model:</b> {model_name}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button("📚 Continue to Books", use_container_width=True, type="primary"):
            st.switch_page("pages/Bookshelf.py")

    with c2:
        if st.button("🧠 Review My Setup", use_container_width=True, type="primary"):
            st.switch_page("pages/Assessment.py")

    with c3:
        if st.button("📊 Open Dashboard", use_container_width=True, type="primary"):
            st.switch_page("pages/Dashboard.py")

    with c4:
        if st.button("🔄 Switch Profile", use_container_width=True, type="secondary"):
            clear_current_user()
            st.rerun()

else:
    left, right = st.columns([1.2, 1], gap="large")

    with left:
        st.markdown(
            """
            <div class="hero-box">
                <div class="hero-title">A reading space that feels bright, calm, and actually made for you.</div>
                <div class="hero-subtitle">
                    Sign in with an existing profile or create a new one. The app keeps your reading setup
                    saved, and the AI recommender can learn from completed sessions to improve later suggestions.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        existing_users = list_users()
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown("### 👤 Sign In")

        if existing_users:
            selected_user = st.selectbox("Choose an existing profile", existing_users, index=0)
            if st.button("Open Profile", use_container_width=True, type="primary"):
                user = get_user_by_username(selected_user)
                if user:
                    load_user_record_into_session(user)
                    update_last_login(user["id"])
                    target_page = "pages/Bookshelf.py" if st.session_state["assessment_completed"] else "pages/Assessment.py"
                    st.switch_page(target_page)
                else:
                    st.error("That profile could not be loaded.")
        else:
            st.info("No saved profiles yet. Create the first one on the right.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown("### ✨ Create New Profile")

        username = st.text_input("Pick a profile name")
        study_consent = st.checkbox(
            "Allow my finished sessions to be used anonymously for improving the recommender",
            value=True,
        )

        # I kept profile names simple here because I did not want real personal details in the app.
        if st.button("Create Profile", use_container_width=True, type="primary"):
            cleaned_username = re.sub(r"[^A-Za-z0-9_-]", "", username.strip())

            if not cleaned_username:
                st.warning("Please enter a profile name using letters or numbers.")
            else:
                try:
                    user = create_user(cleaned_username, study_consent)
                    load_user_record_into_session(user)
                    st.switch_page("pages/Assessment.py")
                except ValueError as exc:
                    st.error(str(exc))

        model_info = get_model_details()
        st.write("")
        st.caption(
            "The recommender starts with a fallback setup and gets stronger after you collect real completed sessions."
        )
        if model_info:
            st.caption(f'Current trained model: {model_info["model_name"]}')
        else:
            st.caption("No trained model saved yet.")
        st.markdown("</div>", unsafe_allow_html=True)