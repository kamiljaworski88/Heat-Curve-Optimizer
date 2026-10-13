"""Regression tests for restart persistence and disconnected sensors.

A minimal fake Home Assistant runtime tests the real coordinator class, not
only its pure analyzer. No external services or user credentials are required.
"""
import asyncio
from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "custom_components.heat_curve_optimizer"

def _coordinator_class(monkeypatch, stored, states):
    class FakeStore:
        saved = None
        def __init__(self, *args):
            pass
        async def async_load(self):
            return stored
        async def async_save(self, data):
            self.saved = data

    def track(hass, callback, interval):
        hass.callback = callback
        return lambda: setattr(hass, "cancelled", True)

    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = type("HomeAssistant", (), {})
    event = types.ModuleType("homeassistant.helpers.event")
    event.async_track_time_interval = track
    storage = types.ModuleType("homeassistant.helpers.storage")
    storage.Store = FakeStore
    for name, module in [
        ("homeassistant", types.ModuleType("homeassistant")),
        ("homeassistant.core", core),
        ("homeassistant.helpers", types.ModuleType("homeassistant.helpers")),
        ("homeassistant.helpers.event", event),
        ("homeassistant.helpers.storage", storage),
    ]:
        monkeypatch.setitem(sys.modules, name, module)
    name = f"{PACKAGE}.coordinator"
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "custom_components" / "heat_curve_optimizer" / "coordinator.py"
    )
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    class States:
        def get(self, entity):
            value = states.get(entity)
            return None if value is None else types.SimpleNamespace(state=value)
    hass = types.SimpleNamespace(states=States(), cancelled=False)
    entry = types.SimpleNamespace(entry_id="test", data={
        "outdoor_temperature": "sensor.outdoor",
        "target_temperature": "sensor.target",
        "floor_heating_temperatures": ["sensor.aqara"],
        "radiator_temperatures": ["sensor.supla"],
        "sample_interval_minutes": 5, "analysis_hours": 24,
    })
    return module.HeatCurveOptimizerCoordinator, hass, entry

def _states():
    return {"sensor.outdoor": "3", "sensor.target": "22",
            "sensor.aqara": "21.4", "sensor.supla": "21.5"}

def test_restart_discards_old_samples(monkeypatch):
    old = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    klass, hass, entry = _coordinator_class(monkeypatch, {
        "samples": [{"timestamp": old, "valid": True, "outdoor": 3.0,
                     "target": 22.0, "floor": [21.0], "radiator": [21.0]}]
    }, _states())
    coordinator = klass(hass, entry)
    asyncio.run(coordinator.async_initialize())
    assert len(coordinator.samples) == 1
    assert coordinator.result["status"] == "insufficient_data"
    asyncio.run(coordinator.async_shutdown())
    assert hass.cancelled

def test_disconnect_blocks_recommendation_and_recovery(monkeypatch):
    values = _states()
    klass, hass, entry = _coordinator_class(monkeypatch, None, values)
    coordinator = klass(hass, entry)
    asyncio.run(coordinator.async_initialize())
    values["sensor.supla"] = "unavailable"
    asyncio.run(coordinator.async_collect())
    assert coordinator.result["status"] == "invalid_data"
    assert "adjustment" not in coordinator.result
    assert coordinator.result["issues"]
    values["sensor.supla"] = "21.5"
    asyncio.run(coordinator.async_collect())
    assert coordinator.result["status"] == "insufficient_data"
    asyncio.run(coordinator.async_shutdown())
