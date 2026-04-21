from html import escape

import streamlit as st

from story_library import BOOKS


def get_books() -> list[dict]:
    return BOOKS


def get_book_by_id(book_id: str) -> dict | None:
    return next((book for book in BOOKS if book["id"] == book_id), None)


def render_book_cover(title: str, shelf: str, cover_style: str) -> None:
    safe_title = escape(title)
    safe_shelf = escape(shelf)

    st.markdown(
        f"""
        <div class="book-cover" style="background:{cover_style};">
            <div>
                <div style="font-size:1.2rem; font-weight:800;">{safe_title}</div>
                <div style="margin-top:0.5rem; font-size:0.9rem; opacity:0.95;">{safe_shelf}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )