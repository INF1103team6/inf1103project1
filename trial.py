"""
Fake / canned implementations of each manager's public functions, built strictly
from contracts.md and tests/sample_input.json.

WHY THIS FILE EXISTS: it's what lets all five people work in parallel from day one
without waiting for anyone else's real code to exist. If you're building
logic_manager_rules and you need something that "looks like" what
logic_manager_judgment will eventually produce, you import fake_assess_severity()
from here instead of blocking on Person 3's actual implementation. Same pattern
in every direction.

Rules for this file:
- Every fake_* function has the exact same name+signature+return shape as the real
  function it stands in for (see contracts.md).
- Fakes never call the network, never touch the filesystem beyond reading
  sample_input.json, and always return instantly.
- When your own real function is ready, you keep using fakes for the OTHER
  modules' functions in your unit tests, and only main.py (Person 5, once
  everything is merged) wires the real functions together end-to-end.
- Nobody edits someone else's "owned" fake without flagging it in the team chat —
  same one-file-shared-carefully rule as any other shared contract.
"""

import json
import os

_SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "tests", "sample_input.json")

with open(_SAMPLE_PATH, "r", encoding="utf-8") as f:
    _SAMPLES = json.load(f)


# ---- stands in for ai_manager.py (Person 2) --------------------------------

def fake_enrich_record(record: dict) -> dict:
    """Returns a canned enriched_record matching contracts.md section 2.
    Looks up by description so tests stay readable."""
    for candidate in _SAMPLES["enriched_records"]:
        if candidate["description"] == record.get("description"):
            return dict(candidate)
    # fallback: no weather enrichment, contract-shaped
    out = dict(record)
    out.update({
        "weather_available": False,
        "condition": None,
        "temperature_c": None,
        "humidity_pct": None,
        "enrichment_error": None,
    })
    return out


# ---- stands in for logic_manager_judgment.py (Person 3) --------------------

def fake_assess_severity(record: dict, weather_data: dict | None = None) -> dict:
    """Returns a canned assessed_record matching contracts.md section 3."""
    for candidate in _SAMPLES["assessed_records"]:
        if candidate["description"] == record.get("description"):
            return dict(candidate)
    out = dict(record)
    out.update({
        "hazard_type": "other",
        "severity_estimate": 1,
        "likelihood_recurrence": "low",
        "assessment_error": None,
    })
    return out


# ---- stands in for data_manager.py (Person 5) -------------------------------

def fake_load_records() -> list:
    return [dict(r) for r in _SAMPLES["assessed_records"]]


def fake_query_by_location(location: str, days: int) -> list:
    if location == "Site A - Block 3":
        return [dict(r) for r in _SAMPLES["history_examples"]["site_a_block_3_recent"]]
    return []


def fake_save_record(record: dict) -> None:
    # no-op: fakes never touch the filesystem
    return None


# ---- stands in for logic_manager_rules.py (Person 4) ------------------------

def fake_decide_outcome(record: dict, history: list) -> str:
    severity = record.get("severity_estimate", 0)
    injury = record.get("injury", False)
    recurrence = record.get("likelihood_recurrence", "unknown")
    if severity >= 4 or (injury and recurrence == "high"):
        return "stop_work_review"
    if len(history) >= 3:
        return "systemic_escalation"
    if record.get("assessment_error"):
        return "pending_review"
    return "log_only"