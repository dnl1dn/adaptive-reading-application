import streamlit as st

from audio_utils import read_aloud


def render_progress(step_no: int, step_name: str):
    return


def audio_prompt_button(text_to_read: str, key: str):
    if st.button("🔊", key=key, type="secondary", help="Read this aloud"):
        read_aloud(text_to_read)


def render_question_row(question_text: str, key: str):
    col1, col2 = st.columns([0.92, 0.08])
    with col1:
        st.markdown(f"**{question_text}**")
    with col2:
        audio_prompt_button(question_text, key)


def render_nav_buttons(buttons):
    cols = st.columns(len(buttons))
    for col, (label, target) in zip(cols, buttons):
        with col:
            if st.button(label, use_container_width=True, type="primary"):
                st.switch_page(target)