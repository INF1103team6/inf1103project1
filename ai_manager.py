"""
ai_manager.py
AI Processing Layer — Workplace Safety Incident Triage System.
extract_hazard_context_flags() is called for EVERY incident and is the
mandatory "AI is the core engine" call (models: GEMINI_MODELS below). When
weather is not relevant, find_similar_incidents() also calls Gemini as a
second, domain-specific use of AI, and search_web_for_similar_incidents()
calls Groq (GPT-OSS with its browser_search tool) for every incident to
find similar real incidents on the internet and whether the hazard is a
known industry problem. Every AI reply is checked with _validate_schema()
before it is used. Zero domain judgment lives here — only
data gathering, API calls, and validation. logic_manager.py is where
judgment happens.
"""

import os
import json
from datetime import datetime

import requests
from dotenv import load_dotenv
from google import genai
import INF1103_Project_Folders.inf1103secret.data_manager as data_manager

load_dotenv()

# Tried in order. Each model has its own free-tier quota, so if one is out
# of quota, overloaded or times out, the next one is tried.
AI_SEED = 42

GEMINI_MODELS = ("gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-lite-latest")

# Groq models with the built-in browser_search tool, tried in order.
# (groq/compound was decommissioned on 21 Sep 2026.)
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_SEARCH_MODELS = ("openai/gpt-oss-120b", "openai/gpt-oss-20b")

# Every incident in this system is on a Singapore construction site, so the
# weather API is called for Singapore regardless of which site logged the
# incident. Keeps the weather call simple instead of geocoding free-text
# site names.
_SG_LATITUDE = 1.3521
_SG_LONGITUDE = 103.8198

# Allowed values for the AI's structured output. These are vocabulary for
# schema validation only — what each value means for severity is decided
# in logic_manager.py, not here.
HAZARD_CATEGORIES = (
    "fall", "fall_from_height", "electrical", "chemical", "vehicular",
    "struck_by_machinery", "low_visibility", "other",
)
INJURY_SEVERITIES = ("none", "minor", "serious", "fatal", "unspecified")

_WEATHER_KEYWORDS = (
    "rain", "wet", "storm", "wind", "windy", "flood", "lightning",
    "thunder", "haze", "hot", "heat", "humid",
)

def is_weather_relevant(record):
    """Checks hazard keywords in the description to decide if weather
    context matters. Simple keyword match — skips the API call otherwise."""
    description = record.get("description", "").lower()
    return any(keyword in description for keyword in _WEATHER_KEYWORDS)