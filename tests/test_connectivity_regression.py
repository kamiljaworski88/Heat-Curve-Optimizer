"""Simulated restart and connectivity regression tests (not a real HA reboot)."""
from custom_components.heat_curve_optimizer.validation import validate_sample
from custom_components.heat_curve_optimizer.algorithm import analyze

def sample(aqara="21.4", supla="21.5"):
    return validate_sample({"outdoor":"3.0","target":"22.0",
        "floor":[("sensor.aqara_floor",aqara)],
        "radiator":[("sensor.supla_radiator",supla)]})

def test_disconnected_aqara_suppresses_recommendation():
    history=[sample() for _ in range(23)]
    history.append(sample(aqara="unavailable"))
    assert not history[-1]["valid"]
    # Coordinator must also suppress recommendation on latest invalid reading.
    assert "adjustment" not in analyze(history[-1:],24)

def test_reconnection_requires_fresh_window():
    history=[sample(aqara="unavailable") for _ in range(20)]
    history.extend(sample() for _ in range(4))
    result=analyze(history,24)
    assert result["status"]=="insufficient_data"

def test_simulated_restart_without_history():
    # Coordinator discards untimestamped legacy samples on restart.
    result=analyze([sample()],24)
    assert result["status"]=="insufficient_data"

def test_recovered_sensors_allow_recommendation_after_full_window():
    history=[sample() for _ in range(24)]
    result=analyze(history,24)
    assert result["status"]=="ready"
