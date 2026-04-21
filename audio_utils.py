import threading
import webbrowser

import pyttsx3
import speech_recognition as sr
import streamlit as st


class TTSManager:
    # I kept the speech part in one class because it was easier to stop and restart cleanly that way.
    def __init__(self):
        self._lock = threading.Lock()
        self._engine = None
        self._thread = None

    def _build_engine(self, rate: int):
        engine = pyttsx3.init()
        engine.setProperty("rate", rate)
        engine.setProperty("volume", 1.0)
        return engine

    def _run_speech(self, text: str, rate: int):
        with self._lock:
            self._engine = self._build_engine(rate)
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

    def speak(self, text: str, rate: int):
        if not text or not text.strip():
            return
        self.stop()
        self._thread = threading.Thread(
            target=self._run_speech,
            args=(text, rate),
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        with self._lock:
            if self._engine is not None:
                try:
                    self._engine.stop()
                except Exception:
                    pass
                self._engine = None


@st.cache_resource
def get_tts_manager():
    return TTSManager()


def read_aloud(text: str):
    rate = int(st.session_state.get("tts_speed", 165))
    get_tts_manager().speak(text, rate)


def stop_reading():
    get_tts_manager().stop()


recognizer = sr.Recognizer()


def listen_once():
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


def search_web(query: str):
    if query and query.strip():
        url = f"https://www.google.com/search?q={query.strip().replace(' ', '+')}"
        webbrowser.open(url)