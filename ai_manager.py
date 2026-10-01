import os
import json
from datetime import datetime

import requests
from dotenv import load_dotenv
from google import genai
import INF1103_Project_Folders.inf1103secret.data_manager as data_manager

load_dotenv()


def is_weather_relevant(record):
    """Checks hazard keywords in the description to decide if weather
    context matters. Simple keyword match — skips the API call otherwise."""
    description = record.get("description", "").lower()
    return any(keyword in description for keyword in _WEATHER_KEYWORDS)


def call_weather_api(location):
    """Calls Open-Meteo (free, no key needed) for current Singapore weather.
    Returns a dict or None on failure — never raises uncaught."""
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": _SG_LATITUDE,
                "longitude": _SG_LONGITUDE,
                "current": "temperature_2m,relative_humidity_2m,precipitation",
                "timezone": "Asia/Singapore",
            },
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})
        precipitation = current.get("precipitation", 0) or 0
        return {
            "condition": "rain" if precipitation > 0 else "clear",
            "temperature_c": current.get("temperature_2m"),
            "humidity_pct": current.get("relative_humidity_2m"),
        }
    except Exception:
        return None


def validate_weather_response(response):
    """Checks condition, temperature_c, humidity_pct are present and
    sensible."""
    if not isinstance(response, dict):
        return False
    condition = response.get("condition")
    temperature_c = response.get("temperature_c")
    humidity_pct = response.get("humidity_pct")
    if condition not in ("rain", "clear"):
        return False
    if not isinstance(temperature_c, (int, float)) or not (-10 <= temperature_c <= 50):
        return False
    if not isinstance(humidity_pct, (int, float)) or not (0 <= humidity_pct <= 100):
        return False
    return True


def classify_lighting_condition(time_of_day, condition):
    """One step darker than time_of_day if weather cuts visibility. Reads
    condition from Darrel's own weather response. Never returns None."""
    levels = ["daylight", "low_light", "dark"]
    base = {"day": 0, "dusk_dawn": 1, "night": 2}.get(time_of_day, 0)
    if condition == "rain":
        base += 1
    base = min(base, len(levels) - 1)
    return levels[base]
