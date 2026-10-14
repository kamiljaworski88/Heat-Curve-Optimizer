"""Sample collection and conservative local persistence."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from .algorithm import analyze
from .const import (
    CONF_ANALYSIS_HOURS, CONF_FLOOR_TEMPS, CONF_OUTDOOR_TEMP, CONF_RADIATOR_TEMPS,
    CONF_SAMPLE_INTERVAL, CONF_TARGET_TEMP, DEFAULT_ANALYSIS_HOURS,
    DEFAULT_SAMPLE_INTERVAL, DOMAIN, STORAGE_SCHEMA_VERSION, STORAGE_VERSION,
)
from .validation import validate_sample
from .learning import build_house_profile, estimate_response_hours, evaluate_change, recommendation_snapshot, new_change

class HeatCurveOptimizerCoordinator:
    def __init__(self, hass: HomeAssistant, entry):
        self.hass, self.entry = hass, entry
        self.samples = []
        self.collection_enabled = False
        self.result = self._paused_result()
        self.issues = []
        self.recommendation_history = []
        self.applied_change = None
        self._listeners = []
        self._unsub = None
        self._store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}")

    def _paused_result(self):
        return {
            "status": "paused",
            "coverage": 0.0,
            "confidence": 0.0,
            "data_quality": "paused",
            "issues": [],
            "reason": "Data collection is paused. Enable it when heating is running.",
        }

    async def async_initialize(self):
        stored = await self._store.async_load()
        # Schema v1 had no collection switch, so its samples may include periods
        # with heating disabled. Discard them once instead of contaminating the
        # first controlled analysis window.
        if isinstance(stored, dict) and stored.get("schema_version") == STORAGE_SCHEMA_VERSION:
            if isinstance(stored.get("samples"), list):
                self.samples = [s for s in stored["samples"] if isinstance(s, dict)]
            self.collection_enabled = bool(stored.get("collection_enabled", False))
            self.recommendation_history = [x for x in stored.get("recommendation_history", []) if isinstance(x, dict)][-500:]
            self.applied_change = stored.get("applied_change") if isinstance(stored.get("applied_change"), dict) else None
        else:
            self.samples = []
            self.collection_enabled = False

        if self.collection_enabled:
            await self.async_collect()
        else:
            self.result = self._paused_result()
            await self._save()

        interval = self.entry.data.get(CONF_SAMPLE_INTERVAL, DEFAULT_SAMPLE_INTERVAL)
        self._unsub = async_track_time_interval(
            self.hass, self._scheduled_collect, timedelta(minutes=interval)
        )

    async def async_shutdown(self):
        if self._unsub:
            self._unsub()
            self._unsub = None
        await self._save()

    async def _save(self):
        await self._store.async_save({
            "schema_version": STORAGE_SCHEMA_VERSION,
            "samples": self.samples,
            "collection_enabled": self.collection_enabled,
            "recommendation_history": self.recommendation_history[-500:],
            "applied_change": self.applied_change,
        })

    def async_add_listener(self, callback):
        self._listeners.append(callback)
        def remove():
            if callback in self._listeners:
                self._listeners.remove(callback)
        return remove

    def _notify_listeners(self):
        for listener in list(self._listeners):
            listener()

    async def async_set_collection_enabled(self, enabled: bool):
        enabled = bool(enabled)
        if self.collection_enabled == enabled:
            return
        self.collection_enabled = enabled
        if enabled:
            await self.async_collect()
            return
        # Keep already collected valid history. While paused no new sample is
        # written and coverage cannot increase.
        self.result = self._paused_result()
        await self._save()
        self._notify_listeners()

    async def _scheduled_collect(self, now):
        if self.collection_enabled:
            await self.async_collect()

    def _state(self, entity_id):
        state = self.hass.states.get(entity_id) if entity_id else None
        return None if state is None else state.state

    async def async_collect(self):
        if not self.collection_enabled:
            self.result = self._paused_result()
            await self._save()
            self._notify_listeners()
            return

        data = self.entry.data
        now = datetime.now(timezone.utc)
        raw = {
            "outdoor": self._state(data.get(CONF_OUTDOOR_TEMP)),
            "target": self._state(data.get(CONF_TARGET_TEMP)),
            "floor": [(e, self._state(e)) for e in data.get(CONF_FLOOR_TEMPS, [])],
            "radiator": [(e, self._state(e)) for e in data.get(CONF_RADIATOR_TEMPS, [])],
        }
        sample = validate_sample(raw)
        self.issues = sample.pop("errors", [])
        sample["timestamp"] = now.isoformat()
        interval = data.get(CONF_SAMPLE_INTERVAL, DEFAULT_SAMPLE_INTERVAL)
        hours = data.get(CONF_ANALYSIS_HOURS, DEFAULT_ANALYSIS_HOURS)
        expected = max(1, int(hours * 60 / interval))
        cutoff = now - timedelta(hours=hours)
        retained = []
        for previous in self.samples:
            try:
                timestamp = datetime.fromisoformat(previous["timestamp"])
                if timestamp.tzinfo is not None and cutoff <= timestamp <= now:
                    retained.append(previous)
            except (KeyError, TypeError, ValueError):
                continue
        self.samples = (retained + [sample])[-max(expected * 2, 48):]
        self.result = analyze(self.samples, expected)
        snapshot = recommendation_snapshot(self.result, now.isoformat())
        if snapshot:
            self.recommendation_history.append(snapshot)
            self.recommendation_history = self.recommendation_history[-500:]
            self.result["house_profile"] = build_house_profile(self.recommendation_history)
            self.result["estimated_response_hours"] = estimate_response_hours(self.recommendation_history)
            self.result["change_evaluation"] = evaluate_change(self.applied_change, self.recommendation_history)
        if self.issues:
            self.result["data_quality"] = "error"
            self.result["issues"] = self.issues
            self.result["status"] = "invalid_data"
            self.result.pop("adjustment", None)
        else:
            self.result["data_quality"] = "ok"
            self.result["issues"] = []
        await self._save()
        self._notify_listeners()

    async def async_register_applied_change(self, adjustment: float):
        """Register a change explicitly confirmed by the user."""
        if self.result.get("status") != "ready":
            return False
        self.applied_change = new_change(adjustment, self.result)
        await self._save()
        self._notify_listeners()
        return True
