"""Pure analysis logic for Heat Curve Optimizer."""
from __future__ import annotations
from statistics import fmean, pstdev
from .const import DEADBAND, MAX_ADJUSTMENT, MIN_COVERAGE, SMALL_ERROR

def analyze(samples: list[dict], expected_samples: int) -> dict:
    valid = [s for s in samples if s.get("valid")]
    coverage = min(1.0, len(valid) / max(1, expected_samples))
    if coverage < MIN_COVERAGE:
        return {"status":"insufficient_data","coverage":coverage,"confidence":0.0,
                "reason":"Not enough valid samples for a safe recommendation."}
    outdoor = [s["outdoor"] for s in valid]
    if len(outdoor) > 1 and pstdev(outdoor) > 3.0:
        return {"status":"unstable_conditions","coverage":coverage,"confidence":0.2,
                "reason":"Outdoor temperature varied too much during the analysis window."}

    target = fmean(s["target"] for s in valid)
    zones = {}
    for key in ("floor","radiator"):
        vals=[v for s in valid for v in s.get(key,[]) if v is not None]
        if vals:
            avg=fmean(vals)
            zones[key]={"average":round(avg,2),"error":round(target-avg,2)}

    if not zones:
        return {"status":"invalid_data","coverage":coverage,"confidence":0.0,
                "reason":"No valid room temperature remains."}

    worst=max(zones.values(), key=lambda z: abs(z["error"]))
    error=worst["error"]
    if abs(error) <= DEADBAND:
        adjustment=0.0
    elif abs(error) <= SMALL_ERROR:
        adjustment=1.0 if error > 0 else -1.0
    else:
        adjustment=MAX_ADJUSTMENT if error > 0 else -MAX_ADJUSTMENT

    confidence=max(0.0,min(1.0,coverage * (1.0-min(pstdev(outdoor) if len(outdoor)>1 else 0,3)/6)))
    return {"status":"ready","coverage":coverage,"confidence":round(confidence,2),
            "outdoor_average":round(fmean(outdoor),2),"target_average":round(target,2),
            "zones":zones,"error":round(error,2),"adjustment":adjustment,
            "reason":"Recommendation is based on the zone furthest from target."}
