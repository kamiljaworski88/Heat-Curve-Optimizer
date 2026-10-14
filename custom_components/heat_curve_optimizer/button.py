"""Button entities for Heat Curve Optimizer."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AppliedRecommendationButton(coordinator, entry)])


class AppliedRecommendationButton(ButtonEntity):
    """Register that the user actually applied the current recommendation."""

    _attr_has_entity_name = True
    _attr_name = "I applied the recommendation"
    _attr_icon = "mdi:check-circle-outline"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_applied_recommendation"

    @property
    def available(self) -> bool:
        result = self.coordinator.result
        return result.get("status") == "ready" and result.get("adjustment") not in (None, 0)

    async def async_press(self) -> None:
        adjustment = self.coordinator.result.get("adjustment")
        if adjustment in (None, 0):
            return
        await self.coordinator.async_register_applied_change(float(adjustment))
