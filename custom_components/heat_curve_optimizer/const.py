"""Constants for Heat Curve Optimizer."""
DOMAIN = "heat_curve_optimizer"
NAME = "Heat Curve Optimizer"
VERSION = "0.5.0"

CONF_OUTDOOR_TEMP = "outdoor_temperature"
CONF_FLOOR_TEMPS = "floor_heating_temperatures"
CONF_RADIATOR_TEMPS = "radiator_temperatures"
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
MAX_ADJUSTMENT = 2.0
STORAGE_VERSION = 1
STORAGE_SCHEMA_VERSION = 2

# Broad physical sanity limits. Values outside them are rejected, never clamped.
MIN_TEMP_C = -60.0
MAX_TEMP_C = 90.0
MIN_INDOOR_C = 5.0
MAX_INDOOR_C = 40.0
MIN_TARGET_C = 5.0
MAX_TARGET_C = 35.0
