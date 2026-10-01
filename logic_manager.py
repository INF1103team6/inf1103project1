def assess_severity(record, weather_data=None, history=None):
    if weather_data is None:
        weather_data = {}
    if history is None:
        history = []

    result = dict(record)

    if record.get("context_flags_error") or record.get("hazard_category") is None:
        result["hazard_type"] = "unassessed"
        result["severity_estimate"] = 0
        result["likelihood_recurrence"] = "unknown"
        result["severity_reasons"] = []
        result["assessment_error"] = (
            "Cannot judge severity without AI hazard extraction: "
            f"{record.get('context_flags_error') or 'hazard_category missing'}"
        )
        return result

    hazard_type = record["hazard_category"]
    injury_severity = record.get("injury_severity", "unspecified")
    at_height = record.get("working_at_height")
    machinery = record.get("heavy_machinery_present")
    ppe_not_worn = record.get("ppe_status") == "not_worn"
    poor_light = record.get("lighting_condition") in ("dark", "low_light")
    similar = record.get("similar_incidents") or []
    similar_escalated = any(item.get("outcome") in _ESCALATED_OUTCOMES for item in similar)
    severity = 1
    reasons = []
    if injury_severity == "fatal":
        severity = 5
        reasons.append("Someone died (set to 5)")
    else:
        injury_points = _INJURY_POINTS.get(injury_severity, 0)
        if injury_points:
            severity += injury_points
            reasons.append(f"{injury_severity.capitalize()} injury (+{injury_points})")
        if record.get("injury") and injury_severity in ("none", "unspecified"):
            severity += 1
            reasons.append("Someone was hurt, but how badly wasn't described (+1)")
    if hazard_type in _TYPE_A_HAZARDS:
        severity += 1
        reasons.append("One of MOM's highest-risk hazard types (+1)")
    if at_height:
        severity += 1
        reasons.append("Working at height (+1)")
    if machinery and ppe_not_worn:
        severity += 1
        reasons.append("Heavy machinery around, without safety gear (+1)")
    if ppe_not_worn:
        severity += 1
        reasons.append("Safety gear (PPE) not worn (+1)")
    elif record.get("ppe_status") == "worn":
        severity -= 1
        reasons.append("Safety gear (PPE) was worn (-1)")
    if poor_light:
        severity += 1
        reasons.append("Poor lighting or dark (+1)")
    if weather_data.get("condition") == "rain" and (at_height or machinery):
        severity += 1
        reasons.append("Raining during work at height or with machinery (+1)")
    if similar_escalated:
        severity += 1
        reasons.append("A similar past incident on our sites was escalated (+1)")
    severity = max(1, min(severity, 5))
    recurrence = "low"
    if poor_light or len(history) >= 1:
        recurrence = "medium"
    if severity >= 4 or len(history) >= 3 or similar_escalated:
        recurrence = "high"

    result["hazard_type"] = hazard_type
    result["severity_estimate"] = severity
    result["likelihood_recurrence"] = recurrence
    result["severity_reasons"] = reasons
    result["assessment_error"] = None
    return result