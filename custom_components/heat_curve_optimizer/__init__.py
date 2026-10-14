"""Heat Curve Optimizer integration."""
from __future__ import annotations

from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import HeatCurveOptimizerCoordinator

PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.BUTTON]
FRONTEND_URL = "/heat_curve_optimizer/heat-curve-fastmile-card.js"
FRONTEND_FILE = Path(__file__).parent / "frontend" / "heat-curve-fastmile-card.js"


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Expose the bundled FastMile card and register it as a Lovelace module."""
    if hass.data.get(DOMAIN, {}).get("_frontend_registered"):
        return

    await hass.http.async_register_static_paths(
        [StaticPathConfig(FRONTEND_URL, str(FRONTEND_FILE), cache_headers=False)]
    )

    resources = hass.data.get("lovelace", {}).get("resources")
    if resources is not None and hasattr(resources, "async_create_item"):
        existing = await resources.async_get_info()
        if not any(item.get("url", "").split("?")[0] == FRONTEND_URL for item in existing):
            await resources.async_create_item({"res_type": "module", "url": FRONTEND_URL})

    hass.data.setdefault(DOMAIN, {})["_frontend_registered"] = True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    await _async_register_frontend(hass)

    coordinator = HeatCurveOptimizerCoordinator(hass, entry)
    await coordinator.async_initialize()
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()
    return unloaded
