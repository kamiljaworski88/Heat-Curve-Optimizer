"""Advanced advisory helpers for v0.6-v0.9."""
from __future__ import annotations
from statistics import fmean

DEADBAND = 0.3

def room_diagnostics(samples: list[dict], target: float) -> dict:
    """Analyse each room independently and detect isolated outliers."""
    values: dict[str, list[float]] = {}
    zones: dict[str, str] = {}
    for sample in samples:
        for zone in ("floor", "radiator"):
            for room in sample.get("rooms", {}).get(zone, []):
                if room.get("value") is None:
                    continue
                values.setdefault(room["entity_id"], []).append(float(room["value"]))
                zones[room["entity_id"]] = zone
    rooms = {}
    for entity_id, readings in values.items():
        avg = fmean(readings)
        rooms[entity_id] = {
            "zone": zones[entity_id],
            "average": round(avg, 2),
            "error": round(target - avg, 2),
            "observations": len(readings),
        }
    cold = [k for k,v in rooms.items() if v["error"] > DEADBAND]
    hot = [k for k,v in rooms.items() if v["error"] < -DEADBAND]
    local_issue = None
    if len(rooms) >= 3:
        if len(cold) == 1 and len(hot) == 0:
            local_issue = {"type": "isolated_underheating", "entity_id": cold[0]}
        elif len(hot) == 1 and len(cold) == 0:
            local_issue = {"type": "isolated_overheating", "entity_id": hot[0]}
    return {"rooms": rooms, "local_issue": local_issue}

def hydraulic_diagnostics(samples: list[dict]) -> dict:
    """Describe supply/return behaviour without pretending to know design delta-T."""
    deltas = []
    supply = []
    ret = []
    for sample in samples:
        s, r = sample.get("supply"), sample.get("return")
        if s is None or r is None:
            continue
        s, r = float(s), float(r)
        supply.append(s); ret.append(r); deltas.append(s-r)
    if not deltas:
        return {"status": "unavailable"}
    avg_delta = fmean(deltas)
    status = "ok"
    if avg_delta < 1.0:
        status = "very_low_delta"
    elif avg_delta > 20.0:
        status = "very_high_delta"
    return {
        "status": status,
        "supply_average": round(fmean(supply),2),
        "return_average": round(fmean(ret),2),
        "delta_t_average": round(avg_delta,2),
        "observations": len(deltas),
    }

def thermostat_diagnostics(samples: list[dict]) -> dict:
    """Flag room-control states that can invalidate a heating-curve conclusion."""
    states = []
    for sample in samples:
        states.extend(str(x).lower() for x in sample.get("thermostats", []) if x is not None)
    if not states:
        return {"status": "unavailable", "blocking": False}
    inactive = {"off", "closed", "idle", "false", "0"}
    inactive_count = sum(s in inactive for s in states)
    ratio = inactive_count / len(states)
    return {
        "status": "controls_inactive" if ratio >= 0.5 else "ok",
        "blocking": ratio >= 0.5,
        "inactive_ratio": round(ratio,2),
        "observations": len(states),
    }

def curve_shape_advice(profile: dict) -> dict:
    """Distinguish likely offset vs slope issues from outdoor-temperature bands."""
    points = []
    for band, data in profile.items():
        if data.get("observations",0) < 3:
            continue
        try:
            low, high = band.replace("C","").split("..")
            midpoint = (float(low)+float(high))/2
            error = float(data["average_error"])
        except (ValueError, KeyError, TypeError):
            continue
        points.append((midpoint,error))
    if len(points) < 2:
        return {"status":"insufficient_profile","recommendation":"wait"}
    points.sort()
    cold_t,cold_e = points[0]
    warm_t,warm_e = points[-1]
    if abs(cold_e) <= DEADBAND and abs(warm_e) <= DEADBAND:
        return {"status":"balanced","recommendation":"no_change"}
    if cold_e > DEADBAND and warm_e > DEADBAND:
        return {"status":"systematically_cold","recommendation":"raise_offset"}
    if cold_e < -DEADBAND and warm_e < -DEADBAND:
        return {"status":"systematically_warm","recommendation":"lower_offset"}
    if cold_e > DEADBAND and abs(warm_e) <= DEADBAND:
        return {"status":"cold_weather_underheating","recommendation":"increase_slope"}
    if abs(cold_e) <= DEADBAND and warm_e < -DEADBAND:
        return {"status":"mild_weather_overheating","recommendation":"increase_slope"}
    if cold_e < -DEADBAND and abs(warm_e) <= DEADBAND:
        return {"status":"cold_weather_overheating","recommendation":"decrease_slope"}
    if abs(cold_e) <= DEADBAND and warm_e > DEADBAND:
        return {"status":"mild_weather_underheating","recommendation":"decrease_slope"}
    return {"status":"mixed","recommendation":"verify_system","cold_error":cold_e,"warm_error":warm_e}
