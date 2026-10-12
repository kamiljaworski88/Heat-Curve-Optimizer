"""Data collection and persistence for Heat Curve Optimizer."""
from __future__ import annotations
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from .algorithm import analyze
from .const import (
    CONF_ANALYSIS_HOURS, CONF_FLOOR_TEMPS, CONF_OUTDOOR_TEMP, CONF_RADIATOR_TEMPS,
    CONF_SAMPLE_INTERVAL, CONF_TARGET_TEMP, DEFAULT_ANALYSIS_HOURS,
    DEFAULT_SAMPLE_INTERVAL, DOMAIN, STORAGE_VERSION,
)
from .validation import validate_sample

class HeatCurveOptimizerCoordinator:
    def __init__(self, hass: HomeAssistant, entry):
        self.hass, self.entry = hass, entry
        self.samples = []
        self.result = {"status":"collecting","coverage":0.0,"confidence":0.0}
        self.issues = []
        self._listeners = []
        self._unsub = None
        self._store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}")

    async def async_initialize(self):
        stored = await self._store.async_load()
        if isinstance(stored, dict):
            self.samples = stored.get("samples", [])
        await self.async_collect()
        interval = self.entry.data.get(CONF_SAMPLE_INTERVAL, DEFAULT_SAMPLE_INTERVAL)
        self._unsub = async_track_time_interval(self.hass, self._scheduled_collect, timedelta(minutes=interval))

    async def async_shutdown(self):
        if self._unsub:
            self._unsub()
            self._unsub = None
        await self._store.async_save({"samples": self.samples})

    def async_add_listener(self, callback):
        self._listeners.append(callback)
        def remove():
            if callback in self._listeners:
                self._listeners.remove(callback)
        return remove

    async def _scheduled_collect(self, now):
        await self.async_collect()

    def _state(self, entity_id):
        state = self.hass.states.get(entity_id) if entity_id else None
        return None if state is None else state.state

    async def async_collect(self):
        data = self.entry.data
        raw = {
            "outdoor": self._state(data.get(CONF_OUTDOOR_TEMP)),
            "target": self._state(data.get(CONF_TARGET_TEMP)),
            "floor": [(e, self._state(e)) for e in data.get(CONF_FLOOR_TEMPS, [])],
            "radiator": [(e, self._state(e)) for e in data.get(CONF_RADIATOR_TEMPS, [])],
        }
        sample = validate_sample(raw)
        self.issues = sample.pop("errors", [])
        self.samples.append(sample)

        interval = data.get(CONF_SAMPLE_INTERVAL, DEFAULT_SAMPLE_INTERVAL)
        hours = data.get(CONF_ANALYSIS_HOURS, DEFAULT_ANALYSIS_HOURS)
        expected = max(1, int(hours * 60 / interval))
        self.samples = self.samples[-max(expected * 2, 48):]
        self.result = analyze(self.samples[-expected:], expected)
        if self.issues:
            self.result["data_quality"] = "error"
            self.result["issues"] = self.issues
            self.result["status"] = "invalid_data"
            self.result.pop("adjustment", None)
        else:
            self.result["data_quality"] = "ok"
            self.result["issues"] = []

        await self._store.async_save({"samples": self.samples})
        for listener in list(self._listeners):
            listener()
