"""Learning helpers for v0.3-v0.5."""
from __future__ import annotations
from datetime import datetime, timezone
from statistics import fmean

def recommendation_snapshot(result: dict, timestamp: str) -> dict | None:
    if result.get("status") != "ready":
        return None
    return {"timestamp": timestamp, "adjustment": float(result.get("adjustment", 0.0)),
            "error": result.get("error"), "outdoor": result.get("outdoor_average"),
            "confidence": result.get("confidence"), "governing_zone": result.get("governing_zone"),
            "zones": result.get("zones", {})}

def outdoor_bucket(value: float, width: int = 5) -> str:
    low = int(value // width) * width
    return f"{low:+d}..{low + width:+d}C"

def build_house_profile(history: list[dict], min_points: int = 3) -> dict:
    groups = {}
    for item in history:
        if item.get("outdoor") is not None and item.get("error") is not None:
            groups.setdefault(outdoor_bucket(float(item["outdoor"])), []).append(item)
    return {bucket: {"observations": len(items),
                     "average_error": round(fmean(float(i["error"]) for i in items), 2),
                     "average_adjustment": round(fmean(float(i.get("adjustment", 0)) for i in items), 2),
                     "average_confidence": round(fmean(float(i.get("confidence", 0)) for i in items), 2)}
            for bucket, items in groups.items() if len(items) >= min_points}

def estimate_response_hours(history: list[dict], min_points: int = 4) -> float | None:
    if len(history) < min_points:
        return None
    delays = []
    for index, start in enumerate(history[:-1]):
        if not start.get("adjustment") or start.get("error") is None or start.get("outdoor") is None:
            continue
        try: started = datetime.fromisoformat(start["timestamp"])
        except (TypeError, ValueError): continue
        for later in history[index + 1:]:
            if later.get("error") is None or later.get("outdoor") is None: continue
            if abs(float(later["outdoor"]) - float(start["outdoor"])) > 2.0: continue
            if abs(float(later["error"])) <= abs(float(start["error"])) - 0.2:
                try: ended = datetime.fromisoformat(later["timestamp"])
                except (TypeError, ValueError): continue
                hours = (ended - started).total_seconds() / 3600
                if 1 <= hours <= 72: delays.append(hours)
                break
    return round(fmean(delays), 1) if delays else None

def evaluate_change(change: dict | None, history: list[dict], min_hours: float = 12.0) -> dict | None:
    if not change: return None
    try: changed_at = datetime.fromisoformat(change["timestamp"])
    except (KeyError, TypeError, ValueError): return None
    before_error, outdoor = change.get("baseline_error"), change.get("outdoor")
    if before_error is None or outdoor is None: return None
    comparable = []
    for item in history:
        try: at = datetime.fromisoformat(item["timestamp"])
        except (KeyError, TypeError, ValueError): continue
        elapsed = (at - changed_at).total_seconds() / 3600
        if elapsed >= min_hours and item.get("error") is not None and item.get("outdoor") is not None and abs(float(item["outdoor"]) - float(outdoor)) <= 2.0:
            comparable.append((elapsed, item))
    if not comparable: return {"status": "waiting", "reason": "Waiting for comparable post-change conditions."}
    elapsed, latest = comparable[-1]
    improvement = round(abs(float(before_error)) - abs(float(latest["error"])), 2)
    outcome = "improved" if improvement >= 0.2 else "worsened" if improvement <= -0.2 else "neutral"
    return {"status": outcome, "hours_since_change": round(elapsed, 1),
            "before_error": round(float(before_error), 2), "after_error": round(float(latest["error"]), 2),
            "improvement": improvement, "applied_adjustment": change.get("adjustment")}

def new_change(adjustment: float, result: dict, timestamp: str | None = None) -> dict:
    return {"timestamp": timestamp or datetime.now(timezone.utc).isoformat(), "adjustment": float(adjustment),
            "baseline_error": result.get("error"), "outdoor": result.get("outdoor_average"),
            "zones": result.get("zones", {})}
