"""Sensors for Heat Curve Optimizer."""
from __future__ import annotations
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        HcoSensor(coordinator, entry, "recommendation", "Recommendation"),
        HcoSensor(coordinator, entry, "temperature_error", "Temperature error", UnitOfTemperature.CELSIUS),
        HcoSensor(coordinator, entry, "confidence", "Confidence", "%"),
        HcoSensor(coordinator, entry, "data_coverage", "Data coverage", "%"),
        HcoSensor(coordinator, entry, "data_quality", "Data quality"),
        HcoSensor(coordinator, entry, "diagnostic_reason", "Diagnostic reason"),
    ])

class HcoSensor(SensorEntity):
    _attr_has_entity_name = True
    def __init__(self, coordinator, entry, key, name, unit=None):
        self.coordinator, self.entry, self.key = coordinator, entry, key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._remove_listener = None

    async def async_added_to_hass(self):
        self._remove_listener = self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        if self._remove_listener:
            self._remove_listener()

    @property
    def native_value(self):
        r = self.coordinator.result
        if self.key == "recommendation":
            if r.get("status") != "ready":
                return r.get("status", "collecting")
            a = r.get("adjustment", 0)
            return "no_change" if a == 0 else ("raise" if a > 0 else "lower")
        if self.key == "temperature_error":
            return r.get("error")
        if self.key == "confidence":
            v = r.get("confidence")
            return round(v * 100) if v is not None else None
        if self.key == "data_coverage":
            v = r.get("coverage")
            return round(v * 100) if v is not None else None
        if self.key == "data_quality":
            return r.get("data_quality", "unknown")
        if self.key == "diagnostic_reason":
            issues = r.get("issues") or []
            return issues[0] if issues else r.get("reason", "OK")

    @property
    def extra_state_attributes(self):
        r = dict(self.coordinator.result)
        if self.key == "recommendation":
            r["recommended_adjustment_c"] = r.get("adjustment")
        return r
