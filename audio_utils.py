import json
import webbrowser

import streamlit as st
import streamlit.components.v1 as components

try:
    import speech_recognition as sr
except Exception:
    sr = None


def _next_tts_nonce() -> int:
    current = int(st.session_state.get("_tts_nonce", 0)) + 1
    st.session_state["_tts_nonce"] = current
    return current


def _browser_rate_from_session() -> float:
    raw_rate = int(st.session_state.get("tts_speed", 165))
    return max(0.5, min(2.0, raw_rate / 165.0))


def _run_browser_tts(action: str, text: str = "", rate: float = 1.0) -> None:
    payload = {
        "action": action,
        "text": text,
        "rate": rate,
        "nonce": _next_tts_nonce(),
    }

    html = f"""
    <script>
        const payload = {json.dumps(payload)};
        const synth = window.parent.speechSynthesis || window.speechSynthesis;

        if (synth) {{
            try {{
                if (payload.action === "stop") {{
                    synth.cancel();
                }}

                if (payload.action === "speak" && payload.text) {{
                    synth.cancel();

                    const utterance = new SpeechSynthesisUtterance(payload.text);
                    utterance.rate = payload.rate;
                    utterance.pitch = 1.0;
                    utterance.volume = 1.0;

                    window.parent.__brightpath_last_utterance = utterance;

                    setTimeout(() => {{
                        try {{
                            synth.speak(utterance);
                        }} catch (err) {{
                            console.log("Speech start failed:", err);
                        }}
                    }}, 40);
                }}
            }} catch (err) {{
                console.log("Browser TTS error:", err);
            }}
        }}
    </script>
    """

    components.html(html, height=0, width=0)


def tts_available() -> bool:
    return True


def voice_input_available() -> bool:
    return sr is not None


def read_aloud(text: str) -> None:
    if not text or not text.strip():
        return

    _run_browser_tts(
        action="speak",
        text=text.strip(),
        rate=_browser_rate_from_session(),
    )


def stop_reading() -> None:
    _run_browser_tts(action="stop")


def listen_once() -> str:
    if sr is None:
        return ""

    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
        return recognizer.recognize_google(audio).strip()
    except Exception:
        return ""


def clean_voice_query(text: str) -> str:
    if not text:
        return ""

    cleaned = text.lower().strip()
    prefixes = ["search for ", "search ", "find ", "look for ", "open "]

    for prefix in prefixes:
        if cleaned.startswith(prefix):
            return cleaned.replace(prefix, "", 1).strip()

    return cleaned


def search_web(query: str) -> None:
    if not query or not query.strip():
        return

    url = f"https://www.google.com/search?q={query.strip().replace(' ', '+')}"
    webbrowser.open(url)
