"""Conservative read-only heating-curve advisory logic."""
from __future__ import annotations
from statistics import fmean, pstdev
from .const import DEADBAND, MAX_ADJUSTMENT, MIN_COVERAGE, SMALL_ERROR

def analyze(samples: list[dict], expected_samples: int) -> dict:
    valid = [s for s in samples if s.get("valid")]
    coverage = min(1.0, len(valid) / max(1, expected_samples))
    base = {"coverage": round(coverage, 3), "confidence": 0.0}
    if coverage < MIN_COVERAGE:
        return {**base, "status": "insufficient_data",
                "reason": "Not enough valid samples for a safe recommendation."}
    outdoor = [s["outdoor"] for s in valid]
    variation = pstdev(outdoor) if len(outdoor) > 1 else 0.0
    if variation > 3.0:
        return {**base, "status": "unstable_conditions",
                "reason": "Outdoor temperature varied too much."}
    target = fmean(s["target"] for s in valid)
    zones = {}
    for key in ("floor", "radiator"):
        # Each sampling instant contributes equally even when sensor counts differ.
        per_sample = [fmean(s[key]) for s in valid if s.get(key)]
        if per_sample:
            average = fmean(per_sample)
            zones[key] = {"average": round(average, 2),
                          "error": round(target - average, 2),
                          "coverage": round(len(per_sample) / max(1, expected_samples), 3)}
    if not zones:
        return {**base, "status": "invalid_data", "reason": "No valid room temperatures."}
    if any(z["coverage"] < MIN_COVERAGE for z in zones.values()):
        return {**base, "status": "insufficient_zone_data", "zones": zones,
                "reason": "One heating zone has insufficient measurements."}
    errors = [z["error"] for z in zones.values()]
    if len(errors) > 1 and max(errors) - min(errors) > 0.8:
        return {**base, "status": "zone_conflict", "zones": zones,
                "reason": "Floor and radiator zones disagree; inspect thermostats and hydraulics."}
    error = fmean(errors)
    adjustment = (0.0 if abs(error) <= DEADBAND else
                  (1.0 if error > 0 else -1.0) if abs(error) <= SMALL_ERROR else
                  (MAX_ADJUSTMENT if error > 0 else -MAX_ADJUSTMENT))
    return {**base, "status": "ready", "zones": zones, "error": round(error, 2),
            "adjustment": adjustment, "confidence": round(coverage * (1 - variation / 6), 2),
            "outdoor_average": round(fmean(outdoor), 2),
            "target_average": round(target, 2),
            "reason": "Preliminary offset suggestion only; not a heating-curve slope calculation."}
