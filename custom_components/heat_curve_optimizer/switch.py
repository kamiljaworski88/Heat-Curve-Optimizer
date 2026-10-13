"""Switch entities for Heat Curve Optimizer."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DataCollectionSwitch(coordinator, entry)])

class DataCollectionSwitch(SwitchEntity):
    """Allow the user to explicitly start and pause sample collection."""

    _attr_has_entity_name = True
    _attr_name = "Data collection"
    _attr_icon = "mdi:database-clock"

    def __init__(self, coordinator, entry):
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_data_collection"
        self._remove_listener = None

    @property
    def is_on(self):
        return self.coordinator.collection_enabled

    async def async_turn_on(self, **kwargs):
        await self.coordinator.async_set_collection_enabled(True)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.async_set_collection_enabled(False)

    async def async_added_to_hass(self):
        self._remove_listener = self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        if self._remove_listener:
            self._remove_listener()
