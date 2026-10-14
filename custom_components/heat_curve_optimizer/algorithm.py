"""Conservative read-only heating-curve advisory logic."""
from __future__ import annotations

from statistics import fmean, pstdev

from .const import (
    DEADBAND,
    MAX_ADJUSTMENT,
    MAX_OUTDOOR_STDDEV,
    MIN_COVERAGE,
    SMALL_ERROR,
)


def _adjustment_for_error(error: float) -> float:
    """Translate a signed room-temperature error into a conservative offset."""
    if abs(error) <= DEADBAND:
        return 0.0
    magnitude = 1.0 if abs(error) <= SMALL_ERROR else MAX_ADJUSTMENT
    return magnitude if error > 0 else -magnitude


def _zone_reason(zones: dict, outdoor_average: float, decision: str) -> str:
    floor = zones.get("floor")
    radiator = zones.get("radiator")
    parts = []
    if floor:
        parts.append(f"floor error {floor['error']:+.2f} °C")
    if radiator:
        parts.append(f"radiator error {radiator['error']:+.2f} °C")
    details = ", ".join(parts)
    if decision == "conflict":
        return (
            f"Zone conflict at outdoor average {outdoor_average:.2f} °C: {details}. "
            "Because both zones share one supply temperature, do not change the curve; "
            "inspect hydraulic balance, valves and room controls."
        )
    if decision == "raise":
        return (
            f"Raise the shared supply/curve offset: {details}. "
            "A clearly underheated zone takes priority while the other zone is not "
            "clearly overheated."
        )
    if decision == "lower":
        return (
            f"Lower the shared supply/curve offset: {details}. "
            "No zone is underheated and at least one zone is clearly overheated."
        )
    return f"Keep the shared supply/curve offset unchanged: {details}."


def analyze(samples: list[dict], expected_samples: int) -> dict:
    valid = [s for s in samples if s.get("valid")]
    coverage = min(1.0, len(valid) / max(1, expected_samples))
    base = {"coverage": round(coverage, 3), "confidence": 0.0}
    if coverage < MIN_COVERAGE:
        return {
            **base,
            "status": "insufficient_data",
            "reason": "Not enough valid samples for a safe recommendation.",
        }

    outdoor = [s["outdoor"] for s in valid]
    variation = pstdev(outdoor) if len(outdoor) > 1 else 0.0
    outdoor_average = fmean(outdoor)
    outdoor_min = min(outdoor)
    outdoor_max = max(outdoor)
    outdoor_range = outdoor_max - outdoor_min
    weather = {
        "outdoor_average": round(outdoor_average, 2),
        "outdoor_min": round(outdoor_min, 2),
        "outdoor_max": round(outdoor_max, 2),
        "outdoor_stddev": round(variation, 2),
    }
    if variation > MAX_OUTDOOR_STDDEV:
        return {
            **base,
            **weather,
            "status": "unstable_conditions",
            "reason": (
                "Outdoor temperature varied too much during the analysis window; "
                "wait for more comparable weather conditions."
            ),
        }

    target = fmean(s["target"] for s in valid)
    zones = {}
    for key in ("floor", "radiator"):
        # Each sampling instant contributes equally even when sensor counts differ.
        per_sample = [fmean(s[key]) for s in valid if s.get(key)]
        if per_sample:
            average = fmean(per_sample)
            zones[key] = {
                "average": round(average, 2),
                # Positive error means underheating; negative means overheating.
                "error": round(target - average, 2),
                "coverage": round(len(per_sample) / max(1, expected_samples), 3),
            }

    if not zones:
        return {**base, **weather, "status": "invalid_data", "reason": "No valid room temperatures."}
    if any(z["coverage"] < MIN_COVERAGE for z in zones.values()):
        return {
            **base,
            **weather,
            "status": "insufficient_zone_data",
            "zones": zones,
            "reason": "One heating zone has insufficient measurements.",
        }

    errors = [z["error"] for z in zones.values()]
    cold = [e for e in errors if e > DEADBAND]
    hot = [e for e in errors if e < -DEADBAND]

    # One shared supply temperature means opposite, material needs must never be
    # averaged into a misleading recommendation.
    if cold and hot:
        return {
            **base,
            **weather,
            "status": "zone_conflict",
            "zones": zones,
            "target_average": round(target, 2),
            "reason": _zone_reason(zones, outdoor_average, "conflict"),
        }

    if cold:
        # Underheating has priority. Use the coldest zone as the limiting zone.
        governing_error = max(cold)
        decision = "raise"
    elif hot:
        # Lower only when no zone needs more heat. Use the hottest zone.
        governing_error = min(hot)
        decision = "lower"
    else:
        governing_error = fmean(errors)
        decision = "no_change"

    adjustment = _adjustment_for_error(governing_error)
    confidence = coverage * max(0.0, 1 - variation / (MAX_OUTDOOR_STDDEV * 2))
    return {
        **base,
        **weather,
        "status": "ready",
        "zones": zones,
        "error": round(governing_error, 2),
        "adjustment": adjustment,
        "confidence": round(confidence, 2),
        "target_average": round(target, 2),
        "governing_zone": max(zones, key=lambda key: zones[key]["error"])
        if decision == "raise"
        else min(zones, key=lambda key: zones[key]["error"])
        if decision == "lower"
        else None,
        "decision_basis": "shared_supply",
        "outdoor_range": round(outdoor_range, 2),
        "reason": _zone_reason(zones, outdoor_average, decision),
    }
