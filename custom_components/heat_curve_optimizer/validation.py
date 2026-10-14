"""Input validation for Heat Curve Optimizer."""
from __future__ import annotations
import math
from .const import MIN_INDOOR_C, MAX_INDOOR_C, MIN_TARGET_C, MAX_TARGET_C, MIN_TEMP_C, MAX_TEMP_C

BAD_STATES={"unknown","unavailable","none",""}

def number(state, label, low=MIN_TEMP_C, high=MAX_TEMP_C):
    if state is None or str(state).strip().lower() in BAD_STATES:
        return None, f"{label}: unavailable"
    try:
        value=float(state)
    except (TypeError, ValueError):
        return None, f"{label}: non-numeric value"
    if not math.isfinite(value):
        return None, f"{label}: non-finite value"
    if not low <= value <= high:
        return None, f"{label}: value {value} outside safe range {low}..{high} °C"
    return value, None

def validate_sample(raw: dict) -> dict:
    errors=[]
    outdoor,e=number(raw.get("outdoor"),"Outdoor temperature")
    if e: errors.append(e)
    target,e=number(raw.get("target"),"Target temperature",MIN_TARGET_C,MAX_TARGET_C)
    if e: errors.append(e)

    zones={}
    rooms={}
    for zone in ("floor","radiator"):
        zones[zone]=[]
        rooms[zone]=[]
        for entity_id,state in raw.get(zone,[]):
            value,e=number(state,entity_id,MIN_INDOOR_C,MAX_INDOOR_C)
            if e: errors.append(e)
            else:
                zones[zone].append(value)
                rooms[zone].append({"entity_id":entity_id,"value":value})

    if not zones["floor"] and not zones["radiator"]:
        errors.append("No valid room temperature sensors")

    supply=None
    if raw.get("supply") is not None:
        supply,e=number(raw.get("supply"),"Supply temperature")
        if e: errors.append(e)
    return_temp=None
    if raw.get("return") is not None:
        return_temp,e=number(raw.get("return"),"Return temperature")
        if e: errors.append(e)

    return {"valid":not errors,"errors":errors,"outdoor":outdoor,"target":target,**zones,
            "rooms":rooms,"supply":supply,"return":return_temp,
            "thermostats":raw.get("thermostats",[])}
