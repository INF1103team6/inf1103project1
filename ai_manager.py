import json

from dotenv import load_dotenv
from google import genai

load_dotenv()

AI_SEED = 42


# Lennart
def _get_gemini_client():
    """Returns a Gemini client, or None if it can't be created (e.g. missing
    GEMINI_API_KEY). Never raises — callers must handle a None client."""
    try:
        # No retries and a 25s timeout per model: _call_gemini() (Ren Xiang)
        # moves on to the next model instead of waiting minutes on a stuck one.
        return genai.Client(http_options={"retry_options": {"attempts": 1}, "timeout": 25000})
    except Exception:
        return None


# Lennart
def _parse_json_safe(text):
    """Best-effort JSON parsing: handles plain JSON and JSON wrapped in
    markdown code fences, which some models add even when asked for a
    JSON mime type."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    return json.loads(cleaned)
