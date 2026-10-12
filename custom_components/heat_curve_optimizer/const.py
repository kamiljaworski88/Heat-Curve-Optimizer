"""Constants for Heat Curve Optimizer."""
from __future__ import annotations

DOMAIN = "heat_curve_optimizer"
NAME = "Heat Curve Optimizer"
VERSION = "0.1.0"

CONF_OUTDOOR_TEMP = "outdoor_temperature"
CONF_INDOOR_TEMPS = "indoor_temperatures"
CONF_TARGET_TEMP = "target_temperature"
CONF_SUPPLY_TEMP = "supply_temperature"
CONF_RETURN_TEMP = "return_temperature"
CONF_POWER = "power"
CONF_OPERATION_STATE = "operation_state"
CONF_HEATING_STATES = "heating_states"
CONF_SAMPLE_INTERVAL = "sample_interval_minutes"
CONF_ANALYSIS_HOURS = "analysis_hours"

DEFAULT_SAMPLE_INTERVAL = 5
DEFAULT_ANALYSIS_HOURS = 24
MIN_COVERAGE = 0.70
MAX_OUTDOOR_STDDEV = 3.0
DEADBAND = 0.3
SMALL_ERROR = 0.8
STORAGE_VERSION = 1
