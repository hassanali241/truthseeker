"""
TruthSeeker — Shared Configuration
====================================
Centralizes environment variable loading and API client initialization.
Supports both local (.env file) and Streamlit Cloud (st.secrets).
"""

import os
from dotenv import load_dotenv

# ── Load environment ───────────────────────────────────────────────
# Supports both local (.env file) and Streamlit Cloud (st.secrets)
load_dotenv()


def _get_secret(key: str) -> str:
    """Read from Streamlit secrets (cloud) or .env (local)."""
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key)


# ── API Keys & URLs ───────────────────────────────────────────────
SUPABASE_URL = _get_secret("SUPABASE_URL")
SUPABASE_KEY = _get_secret("SUPABASE_KEY")
GROQ_API_KEY = _get_secret("GROQ_API_KEY")
TAVILY_API_KEY = _get_secret("TAVILY_API_KEY")
