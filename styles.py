import streamlit as st


def apply_global_styles():
    st.markdown(
        """
        <style>
        body {
            background: linear-gradient(135deg, #eef2ff, #fdf4ff);
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1280px;
        }

        html, body, [class*="css"] {
            font-family: "Segoe UI", sans-serif;
            color: #1e1e2f;
        }

        .hero-box {
            background: linear-gradient(135deg, #ff4da6 0%, #7c4dff 48%, #35c9ff 100%);
            border-radius: 28px;
            padding: 2.6rem;
            color: white;
            box-shadow: 0 20px 45px rgba(124, 77, 255, 0.22);
        }

        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            line-height: 1.08;
            margin-bottom: 0.7rem;
        }

        .hero-subtitle {
            font-size: 1.08rem;
            line-height: 1.75;
            opacity: 0.98;
        }

        .section-title {
            font-size: 1.9rem;
            font-weight: 800;
            margin: 1rem 0;
            color: #2a2a4a;
        }

        .soft-card, .feature-card, .book-card, .result-card {
            background: #ffffff;
            border-radius: 22px;
            padding: 1.25rem;
            box-shadow: 0 12px 28px rgba(31, 41, 55, 0.08);
            border: 1px solid rgba(124, 77, 255, 0.08);
        }

        .soft-card:hover, .feature-card:hover, .book-card:hover {
            transform: translateY(-5px);
            transition: 0.25s ease;
        }

        .feature-title {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
            color: #1e1e2f;
        }

        .feature-text {
            color: #55556b;
            line-height: 1.65;
        }

        .book-cover {
            height: 220px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            font-size: 1.1rem;
            font-weight: 800;
            color: white;
            padding: 1rem;
            margin-bottom: 1rem;
            line-height: 1.4;
        }

        .metric-card {
            background: linear-gradient(135deg, #35c9ff 0%, #7c4dff 100%);
            color: white;
            border-radius: 22px;
            padding: 1.2rem;
            box-shadow: 0 10px 28px rgba(124, 77, 255, 0.18);
        }

        .big-number {
            font-size: 2.2rem;
            font-weight: 800;
            color: #7c4dff;
        }

        .reader-shell {
            background: #fffdf7;
            color: #222;
            border-radius: 22px;
            padding: 2rem;
            box-shadow: 0 12px 32px rgba(31, 41, 55, 0.08);
            border: 1px solid rgba(124, 77, 255, 0.08);
        }

        .small-note {
            color: #66667d;
            font-size: 0.95rem;
        }

        .shelf-badge {
            display: inline-block;
            padding: 0.3rem 0.75rem;
            border-radius: 999px;
            background: #eee7ff;
            color: #5b34b7;
            font-size: 0.82rem;
            font-weight: 700;
            margin-bottom: 0.7rem;
        }

        .highlight-strip {
            background: linear-gradient(135deg, #ffffff 0%, #f6f0ff 100%);
            border-radius: 20px;
            padding: 1rem 1.2rem;
            box-shadow: 0 10px 24px rgba(31, 41, 55, 0.06);
            border: 1px solid rgba(124, 77, 255, 0.08);
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #7c4dff, #35c9ff);
            color: white;
            border-radius: 14px;
            border: none;
            padding: 0.7rem 1rem;
            font-weight: 700;
            box-shadow: 0 8px 20px rgba(124,77,255,0.18);
        }

        .stButton > button[kind="primary"]:hover {
            transform: scale(1.04);
            transition: 0.2s ease;
        }

        .stButton > button[kind="secondary"] {
            background: linear-gradient(135deg, #ff7b54, #ff4da6);
            color: white;
            border-radius: 14px;
            border: none;
            padding: 0.7rem 1rem;
            font-weight: 700;
            box-shadow: 0 8px 20px rgba(255,77,166,0.18);
        }

        .stButton > button[kind="secondary"]:hover {
            transform: scale(1.04);
            transition: 0.2s ease;
        }

        .stTextInput input, .stTextArea textarea {
            background-color: #f8f8ff !important;
            color: #1e1e2f !important;
            border-radius: 10px !important;
        }

        .stSelectbox div[data-baseweb="select"] > div {
            background-color: #f8f8ff !important;
            color: #1e1e2f !important;
            border-radius: 12px !important;
        }

        .stAlert {
            border-radius: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )