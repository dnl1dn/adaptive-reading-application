import threading
import webbrowser

import streamlit as st

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

try:
    import speech_recognition as sr
except Exception:
    sr = None


class TTSManager:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._engine = None
        self._thread = None

    def _build_engine(self, rate: int):
        if pyttsx3 is None:
            return None

        engine = pyttsx3.init()
        engine.setProperty("rate", rate)
        engine.setProperty("volume", 1.0)
        return engine

    def _run_speech(self, text: str, rate: int) -> None:
        with self._lock:
            self._engine = self._build_engine(rate)

            if self._engine is None:
                return

            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception:
                pass
            finally:
                try:
                    self._engine.stop()
                except Exception:
                    pass
                self._engine = None
                self._thread = None

    def speak(self, text: str, rate: int) -> None:
        if pyttsx3 is None or not text or not text.strip():
            return

        self.stop()
        self._thread = threading.Thread(
            target=self._run_speech,
            args=(text, rate),
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        with self._lock:
            if self._engine is not None:
                try:
                    self._engine.stop()
                except Exception:
                    pass
                self._engine = None
            self._thread = None


@st.cache_resource
def get_tts_manager() -> TTSManager:
    return TTSManager()


def tts_available() -> bool:
    return pyttsx3 is not None


def voice_input_available() -> bool:
    return sr is not None


def read_aloud(text: str) -> None:
    if pyttsx3 is None:
        return

    rate = int(st.session_state.get("tts_speed", 165))
    get_tts_manager().speak(text, rate)


def stop_reading() -> None:
    if pyttsx3 is None:
        return

    get_tts_manager().stop()


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
