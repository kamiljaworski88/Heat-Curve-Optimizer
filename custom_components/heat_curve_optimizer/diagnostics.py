"""Diagnostics for Heat Curve Optimizer."""
from __future__ import annotations
from homeassistant.components.diagnostics import async_redact_data
from .const import DOMAIN
TO_REDACT = {"outdoor_temperature","indoor_temperatures","target_temperature","supply_temperature","return_temperature","power","operation_state"}

async def async_get_config_entry_diagnostics(hass, entry):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    return {
        "config": async_redact_data(dict(entry.data), TO_REDACT),
        "analysis": dict(coordinator.result),
        "stored_sample_count": len(coordinator.samples),
    }
