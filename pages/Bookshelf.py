import streamlit as st

from app_state import init_session_state
from audio_utils import clean_voice_query, listen_once, search_web
from book_data import get_books, render_book_cover
from database import init_db
from styles import apply_global_styles
from ui_helpers import render_nav_buttons, render_progress

st.set_page_config(page_title="Books", page_icon="📚", layout="wide")

init_db()
init_session_state()
apply_global_styles()
render_progress(2, "Bookshelf")

if not st.session_state["current_user_id"]:
    st.warning("Please sign in or create a profile first.")
    if st.button("Go to Sign In", type="primary"):
        st.switch_page("main.py")
    st.stop()

st.markdown(
    f"""
    <div class="hero-box" style="padding:2.2rem;">
        <div class="hero-title" style="font-size:2.4rem;">📚 Welcome back, {st.session_state["current_username"]}</div>
        <div class="hero-subtitle">
            Your saved reading setup is loaded, and the same books are here ready to open.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="highlight-strip" style="margin-top:1rem;">
        <b style="color:#1e1e2f;">Current saved profile:</b>
        <span style="color:#5b34b7; font-weight:700;"> {st.session_state["current_profile_label"].replace("_", " ").title()}</span>
        <span style="margin-left:1rem; color:#1e1e2f;"><b>Suggested shelf:</b> {st.session_state["selected_shelf"]}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
st.markdown('<div class="section-title">🎙️ Voice Search</div>', unsafe_allow_html=True)
st.caption("Use your voice if typing feels slower or if you just want a quicker way to search.")

voice_left, voice_right = st.columns([1.2, 0.8], gap="large")

with voice_left:
    if st.button("🎙️ Listen Once", use_container_width=True, type="secondary"):
        heard = listen_once()
        if heard:
            st.session_state["voice_query"] = clean_voice_query(heard)
            st.success(f'I heard: "{heard}"')
        else:
            st.warning("I could not hear anything clearly that time.")

    typed_query = st.text_input(
        "Search books by voice or typing",
        value=st.session_state["voice_query"],
        key="bookshelf_voice_query_box",
    ).strip().lower()

    if typed_query != st.session_state["voice_query"].strip().lower():
        st.session_state["voice_query"] = typed_query

with voice_right:
    if st.button("🌐 Search the Web", use_container_width=True, type="secondary"):
        if st.session_state["voice_query"].strip():
            search_web(st.session_state["voice_query"])
        else:
            st.warning("Say or type something first.")

books = get_books()
query = st.session_state["voice_query"].strip().lower()

if query:
    books = [
        book for book in books
        if query in book["title"].lower()
        or query in book["summary"].lower()
        or query in book["shelf"].lower()
        or query in book["author"].lower()
    ]

st.write("")
st.markdown('<div class="section-title">⭐ Recommended for You</div>', unsafe_allow_html=True)

filter_choice = st.selectbox(
    "Browse by shelf",
    ["All", "Recommended", "Adventure Shelf", "Calm Reads"],
    index=["All", "Recommended", "Adventure Shelf", "Calm Reads"].index(
        st.session_state["selected_shelf"]
        if st.session_state["selected_shelf"] in ["Recommended", "Adventure Shelf", "Calm Reads"]
        else "All"
    ),
)

shelves = ["Recommended", "Adventure Shelf", "Calm Reads"] if filter_choice == "All" else [filter_choice]

for shelf in shelves:
    st.write("")
    st.markdown(f'<div class="section-title">📚 {shelf}</div>', unsafe_allow_html=True)

    shelf_books = [book for book in books if book["shelf"] == shelf]
    cols = st.columns(4, gap="large")

    for i, book in enumerate(shelf_books):
        with cols[i % 4]:
            st.markdown('<div class="book-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="shelf-badge">{book["shelf"]}</div>', unsafe_allow_html=True)
            render_book_cover(book["title"], book["shelf"], book["cover_style"])
            st.markdown(f"**{book['title']}**")
            st.caption(book["author"])
            st.write(book["summary"])

            if st.button(f"Open {book['title']}", key=f"open_{book['id']}", use_container_width=True, type="primary"):
                st.session_state["selected_book"] = book["id"]
                st.session_state["active_session_id"] = None
                st.session_state["active_book_id"] = None
                st.switch_page("pages/BookViewer.py")

            st.markdown("</div>", unsafe_allow_html=True)

st.write("")
render_nav_buttons([
    ("🏠 Sign In", "main.py"),
    ("🧠 My Setup", "pages/Assessment.py"),
    ("📊 Dashboard", "pages/Dashboard.py"),
])