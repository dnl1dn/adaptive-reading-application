import re
from html import escape
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

import streamlit as st

from ai_profiles import apply_profile_to_state, profile_description, profile_title
from app_state import assessment_snapshot_from_state, init_session_state, settings_snapshot_from_state
from audio_utils import clean_voice_query, listen_once, read_aloud, search_web, stop_reading
from book_data import get_book_by_id, render_book_cover
from database import get_user_history_summary, init_db, start_reading_session
from profile_logic import baseline_profile_from_assessment, get_theme_palette
from reading_tools import apply_chunking, get_font_family, get_reading_width_style
from styles import apply_global_styles
from ui_helpers import render_nav_buttons

st.set_page_config(page_title="Book Viewer", page_icon="📖", layout="wide")

init_db()
init_session_state()
apply_global_styles()


@st.cache_data(show_spinner=False)
def fetch_content(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=25) as response:
        return response.read().decode("utf-8", errors="ignore")


@st.cache_data(show_spinner=False)
def fetch_image_urls_from_gutenberg_page(source_url: str) -> list[str]:
    try:
        html = fetch_content(source_url)
    except Exception:
        return []

    pattern = re.compile(
        r'<a[^>]+type=["\']image/[^"\']+["\'][^>]+href=["\']([^"\']+)["\']',
        flags=re.IGNORECASE,
    )
    matches = pattern.findall(html)

    urls: list[str] = []
    for href in matches:
        if href.startswith("http://") or href.startswith("https://"):
            urls.append(href)
        elif href.startswith("/"):
            urls.append(f"https://www.gutenberg.org{href}")
        else:
            urls.append(f"https://www.gutenberg.org/{href.lstrip('/')}")

    seen: set[str] = set()
    deduped: list[str] = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            deduped.append(url)

    return deduped


def clean_text_for_audio(text: str) -> str:
    start = text.find("*** START OF")
    end = text.find("*** END OF")

    if start != -1:
        text = text[start:]
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]

    if end != -1:
        text = text[:end]

    story_markers = [
        "CHAPTER I",
        "CHAPTER I.",
        "I--DOWN THE RABBIT-HOLE",
        "DOWN THE RABBIT-HOLE",
        "STAVE ONE",
        "BOOK I",
        "CHAPTER 1",
    ]

    positions = [text.find(marker) for marker in story_markers if text.find(marker) != -1]
    if positions:
        text = text[min(positions):]

    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


def clean_text_for_reader(text: str) -> str:
    text = clean_text_for_audio(text)

    junk_patterns = [
        r"(?im)^illustration:.*$",
        r"(?im)^produced by.*$",
        r"(?im)^transcriber'?s note:.*$",
    ]
    for pattern in junk_patterns:
        text = re.sub(pattern, "", text)

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


def build_paragraph_html(text: str) -> str:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return "".join(f"<p>{escape(paragraph)}</p>" for paragraph in paragraphs)


def build_reader_style() -> tuple[str, str]:
    palette = get_theme_palette(st.session_state["theme"])
    font_family = get_font_family(st.session_state["font_style"])
    width_style = get_reading_width_style(st.session_state["reading_width"])

    focus_extra = ""
    if st.session_state["focus_mode"]:
        focus_extra = "box-shadow: 0 0 0 6px rgba(124,77,255,0.12);"

    reader_shell_style = "; ".join(
        part.strip().rstrip(";")
        for part in [
            f"background:{palette['bg']}",
            f"color:{palette['text']}",
            width_style,
            focus_extra,
            "padding:1rem",
            "border-radius:22px",
            "box-shadow:0 12px 32px rgba(31, 41, 55, 0.08)",
            "border:1px solid rgba(124, 77, 255, 0.08)",
        ]
        if part and str(part).strip()
    ) + ";"

    text_style = "; ".join(
        part.strip().rstrip(";")
        for part in [
            f"font-size:{int(st.session_state['font_size'])}px",
            f"line-height:{float(st.session_state['spacing'])}",
            f"color:{palette['text']}",
            f"font-family:{font_family}",
            "max-height:720px",
            "overflow-y:auto",
            "padding-right:1rem",
        ]
        if part and str(part).strip()
    ) + ";"

    return reader_shell_style, text_style


def render_story_images(book: dict) -> None:
    if not book.get("source_url"):
        return

    image_urls = fetch_image_urls_from_gutenberg_page(book["source_url"])
    if not image_urls:
        return

    st.write("")
    st.markdown("### 🖼 Story Images")
    st.caption("These are pulled from the book source when image files are available.")

    cols = st.columns(2, gap="large")
    for index, image_url in enumerate(image_urls[:6]):
        with cols[index % 2]:
            st.image(image_url, use_container_width=True)


if not st.session_state["current_user_id"]:
    st.warning("Please sign in or create a profile first.")
    if st.button("Go to Sign In", type="primary"):
        st.switch_page("main.py")
    st.stop()

book = get_book_by_id(st.session_state.get("selected_book"))
if not book:
    st.warning("No book selected yet. Go to the bookshelf first.")
    if st.button("Go to Books", type="primary"):
        st.switch_page("pages/Bookshelf.py")
    st.stop()

is_real_book = book.get("content_mode") == "remote_book"

if is_real_book:
    raw_text = fetch_content(book["text_url"])
    full_book_text = clean_text_for_audio(raw_text)
    reader_text = clean_text_for_reader(raw_text)
else:
    full_book_text = book["content"]
    reader_text = book["content"]

if st.session_state["chunking_mode"] == "Shorter Paragraphs":
    reader_text = apply_chunking(reader_text, st.session_state["chunking_mode"])

if st.session_state.get("active_session_id") is None or st.session_state.get("active_book_id") != book["id"]:
    history = get_user_history_summary(st.session_state["current_user_id"])
    baseline_profile = baseline_profile_from_assessment(
        difficulty=st.session_state["difficulty"],
        confidence=int(st.session_state["confidence"]),
        comprehension=int(st.session_state["comprehension"]),
        speed=int(st.session_state["speed"]),
        keep_place=int(st.session_state["keep_place"]),
        crowded_text=int(st.session_state["crowded_text"]),
        screen_tiredness=int(st.session_state["screen_tiredness"]),
        likes_read_aloud=int(st.session_state["likes_read_aloud"]),
        likes_short_chunks=int(st.session_state["likes_short_chunks"]),
        likes_calm_colours=int(st.session_state["likes_calm_colours"]),
        tts_enabled=bool(st.session_state["tts_enabled"]),
        voice_enabled=bool(st.session_state["voice_enabled"]),
    )
    session_id = start_reading_session(
        user_id=st.session_state["current_user_id"],
        book_id=book["id"],
        recommended_profile=st.session_state.get("ai_recommended_profile", st.session_state["current_profile_label"]),
        recommended_by_ai=st.session_state.get("ai_recommendation_source", "").startswith("trained model"),
        baseline_profile=baseline_profile,
        assessment=assessment_snapshot_from_state(),
        history=history,
        settings_start=settings_snapshot_from_state(),
    )
    st.session_state["active_session_id"] = session_id
    st.session_state["active_book_id"] = book["id"]

st.markdown(
    f"""
    <div class="hero-box" style="padding:2rem;">
        <div class="hero-title" style="font-size:2.2rem;">📖 {escape(book['title'])}</div>
        <div class="hero-subtitle">
            This is the main reading page for the selected book.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

top_left, top_right = st.columns([1, 1], gap="large")

with top_left:
    render_book_cover(book["title"], book["shelf"], book["cover_style"])

with top_right:
    st.markdown(f"**Signed in as:** {escape(st.session_state['current_username'])}")
    st.markdown(f"**Author:** {escape(book['author'])}")
    st.markdown(f"**Shelf:** {escape(book['shelf'])}")
    if is_real_book:
        st.markdown("**Book source:**")
        st.link_button("🔗 Open Book Source", book["source_url"], use_container_width=True)

st.write("")
st.write("")

left, right = st.columns([2, 1], gap="large")

with left:
    reader_shell_style, text_style = build_reader_style()
    paragraph_html = build_paragraph_html(reader_text)

    st.markdown(
        f"""
        <div class="reader-shell" style="{reader_shell_style}">
            <div style="{text_style}">
                {paragraph_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if is_real_book:
        render_story_images(book)

with right:
    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    current_label = st.session_state.get("current_profile_label", "balanced_default")
    rec_label = st.session_state.get("ai_recommended_profile", current_label)
    rec_source = st.session_state.get("ai_recommendation_source", "baseline rules")

    st.markdown("### 🤖 AI Personalisation")
    st.caption("This is the setup the saved profile or recommender picked for you.")
    st.markdown(f"**Current profile:** {profile_title(current_label)}")
    st.markdown(f"**Last recommendation:** {profile_title(rec_label)}")
    st.caption(profile_description(rec_label))
    st.caption(f"Source: {rec_source}")

    if st.button("Apply Recommended Setup Again", use_container_width=True, type="secondary"):
        apply_profile_to_state(rec_label, st.session_state)
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.markdown("### 🎧 Audio Book")
    st.caption("This reads the cleaned text version of the book.")

    old_font = int(st.session_state["font_size"])
    old_spacing = float(st.session_state["spacing"])

    st.session_state["font_size"] = st.slider("Text size", 16, 36, old_font)
    st.session_state["spacing"] = st.slider("Line spacing", 1.0, 2.5, old_spacing, 0.1)

    if old_font != st.session_state["font_size"] or old_spacing != st.session_state["spacing"]:
        st.session_state["setting_changes"] += 1

    if st.button("🔊 Read Book Text", use_container_width=True):
        st.session_state["audio_used"] = True
        read_aloud(full_book_text)

    if st.button("⏹ Stop Reading", use_container_width=True):
        stop_reading()

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.markdown("### 🗣 Custom Text-to-Speech")
    st.caption("This only reads the text typed into the box below.")

    st.text_area(
        "Type or paste your own text",
        height=150,
        key="book_custom_tts_text",
    )

    c1, c2 = st.columns(2)

    with c1:
        if st.button("🎙️ Voice Input", use_container_width=True):
            heard = listen_once()
            if heard:
                st.session_state["book_custom_tts_text"] = clean_voice_query(heard)
                st.success(f'I heard: "{heard}"')
            else:
                st.warning("I could not hear anything clearly that time.")

    with c2:
        if st.button("🌐 Search the Web", use_container_width=True):
            text_to_search = st.session_state.get("book_custom_tts_text", "").strip()
            if text_to_search:
                search_web(text_to_search)
            else:
                search_web(book["title"])

    if st.button("🗣 Read My Custom Text", use_container_width=True):
        text_to_read = st.session_state.get("book_custom_tts_text", "").strip()
        if text_to_read:
            st.session_state["custom_tts_used"] = True
            read_aloud(text_to_read)
        else:
            st.warning("Type some text first.")

    if is_real_book:
        query = quote_plus(f"{book['title']} illustrations")
        st.link_button(
            "🖼 Search More Images",
            f"https://www.google.com/search?tbm=isch&q={query}",
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

st.write("")
render_nav_buttons([
    ("⬅ Back to Books", "pages/Bookshelf.py"),
    ("📝 Feedback", "pages/Feedback.py"),
    ("📊 Dashboard", "pages/Dashboard.py"),
])