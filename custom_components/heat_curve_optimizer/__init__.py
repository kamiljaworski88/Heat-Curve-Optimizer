"""Heat Curve Optimizer integration."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import HeatCurveOptimizerCoordinator

_LOGGER = logging.getLogger(__name__)
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

    # LovelaceData is an object (not a mapping) in modern Home Assistant.
    # In storage mode, register once and preserve all existing resources.
    # In YAML resource mode, the collection is read-only; use the frontend
    # extra module registration rather than modifying the user's YAML.
    try:
        lovelace = hass.data.get("lovelace")
        resources = (
            lovelace.get("resources")
            if isinstance(lovelace, dict)
            else getattr(lovelace, "resources", None)
        )
        if resources is not None and hasattr(resources, "async_create_item"):
            # Important: load persisted resources BEFORE async_items/create.
            # Otherwise creating a resource can overwrite existing entries.
            if not getattr(resources, "loaded", False):
                await resources.async_get_info()
            existing = resources.async_items()
            if not any(
                item.get("url", "").split("?")[0] == FRONTEND_URL
                for item in existing
            ):
                await resources.async_create_item(
                    {"res_type": "module", "url": FRONTEND_URL}
                )
        else:
            add_extra_js_url(hass, FRONTEND_URL)
            _LOGGER.info(
                "FastMile card loaded as frontend module (YAML Lovelace resources)"
            )
    except Exception:
        # Frontend failures must never stop the heating advisor itself.
        _LOGGER.exception("Could not automatically register FastMile card")

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
