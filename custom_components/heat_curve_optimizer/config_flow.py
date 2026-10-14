"""Config flow for Heat Curve Optimizer."""
from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector
from .const import (
    CONF_ANALYSIS_HOURS, CONF_FLOOR_TEMPS, CONF_HEATING_STATES,
    CONF_OPERATION_STATE, CONF_OUTDOOR_TEMP, CONF_POWER, CONF_RADIATOR_TEMPS,
    CONF_RETURN_TEMP, CONF_SAMPLE_INTERVAL, CONF_SUPPLY_TEMP, CONF_TARGET_TEMP, CONF_THERMOSTATS,
    DEFAULT_ANALYSIS_HOURS, DEFAULT_SAMPLE_INTERVAL, DOMAIN, NAME,
)

TEMP_SELECTOR = selector.EntitySelector(
    selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
)
MULTI_TEMP_SELECTOR = selector.EntitySelector(
    selector.EntitySelectorConfig(domain="sensor", device_class="temperature", multiple=True)
)

class HeatCurveOptimizerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            if not user_input.get(CONF_FLOOR_TEMPS) and not user_input.get(CONF_RADIATOR_TEMPS):
                return self.async_show_form(
                    step_id="user", data_schema=self._schema(),
                    errors={"base": "no_heating_zone"},
                )
            return self.async_create_entry(title=user_input.pop(CONF_NAME, NAME), data=user_input)
        return self.async_show_form(step_id="user", data_schema=self._schema())

    def _schema(self):
        return vol.Schema({
            vol.Optional(CONF_NAME, default=NAME): str,
            vol.Required(CONF_OUTDOOR_TEMP): TEMP_SELECTOR,
            vol.Optional(CONF_FLOOR_TEMPS, default=[]): MULTI_TEMP_SELECTOR,
            vol.Optional(CONF_RADIATOR_TEMPS, default=[]): MULTI_TEMP_SELECTOR,
            vol.Required(CONF_TARGET_TEMP): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor", "number", "input_number"])
            ),
            vol.Optional(CONF_SUPPLY_TEMP): TEMP_SELECTOR,
            vol.Optional(CONF_RETURN_TEMP): TEMP_SELECTOR,
            vol.Optional(CONF_POWER): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Optional(CONF_THERMOSTATS, default=[]): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["climate", "binary_sensor", "switch", "sensor"], multiple=True)
            ),
            vol.Optional(CONF_OPERATION_STATE): selector.EntitySelector(selector.EntitySelectorConfig()),
            vol.Optional(CONF_HEATING_STATES, default="heating,heat,on"): str,
            vol.Optional(CONF_SAMPLE_INTERVAL, default=DEFAULT_SAMPLE_INTERVAL):
                vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
            vol.Optional(CONF_ANALYSIS_HOURS, default=DEFAULT_ANALYSIS_HOURS):
                vol.All(vol.Coerce(int), vol.Range(min=12, max=168)),
        })
