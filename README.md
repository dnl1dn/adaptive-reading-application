# Adaptive Reading Application

Adaptive Reading Application is a final year project prototype developed to support personalised digital reading. The system was designed to assess a user’s reading needs, recommend a suitable reading profile, apply accessibility-focused settings, and improve future personalisation through saved feedback and session history.

The project combines a multi-page Streamlit interface, a SQLite database, predefined reading support profiles, and a trained machine learning recommender.

## Project Aim

The aim of the project is to investigate how AI-based personalisation can be used to improve reading accessibility and comfort for users with different reading needs.

## Main Features

- user sign in and saved profiles
- reading needs assessment
- AI-based reading profile recommendation
- predefined personalised reading profiles
- bookshelf and book viewer
- text-to-speech support
- voice input support
- feedback collection after reading
- saved settings and profile updating
- dashboard showing saved profile and AI model information
- model training and training-data export tools

## Reading Profiles

The application currently supports 10 reading profiles:

- `support_large_audio`
- `focus_high_spacing`
- `balanced_default`
- `calm_low_stimulation`
- `independent_wide`
- `audio_guided`
- `memory_support`
- `fatigue_relief`
- `high_contrast_focus`
- `light_audio_support`

These profiles control combinations of settings such as font size, line spacing, theme, reading width, chunking mode, focus mode, text-to-speech, and voice support.

## Core User Flow

1. The user signs in or creates a new profile.
2. The user completes the assessment.
3. The app recommends a reading profile.
4. The user opens a book and reads with the applied settings.
5. The user completes feedback after reading.
6. The app saves session data and can update the user profile.
7. The saved session data can later be used to retrain the AI model.

## Technology Stack

- **Python** for the overall application logic
- **Streamlit** for the user interface
- **SQLite** for local storage of users and sessions
- **scikit-learn** for machine learning models
- **pandas** for data handling
- **joblib** for saving and loading trained models
- **pyttsx3** for text-to-speech
- **SpeechRecognition** for voice input support

## Project Structure

```text
Adaptive Reading Application/
├── .streamlit/
│   └── config.toml
├── models/
│   └── reading_recommender.joblib
├── pages/
│   ├── Assessment.py
│   ├── Bookshelf.py
│   ├── BookViewer.py
│   ├── Dashboard.py
│   └── Feedback.py
├── ai_profiles.py
├── ai_recommender.py
├── app_state.py
├── audio_utils.py
├── book_data.py
├── database.py
├── export_training_data.py
├── main.py
├── profile_logic.py
├── reading_tools.py
├── seed_demo_sessions.py
├── story_library.py
├── styles.py
├── train_recommender.py
├── ui_helpers.py
├── requirements.txt
└── README.md