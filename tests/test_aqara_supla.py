"""Failure and recovery simulations for Aqara and Supla temperature sensors."""
from custom_components.heat_curve_optimizer.validation import validate_sample
from custom_components.heat_curve_optimizer.algorithm import analyze

def raw(aqara="22.0", supla="21.5", outdoor="2.0", target="22.0"):
    return {"outdoor":outdoor,"target":target,
            "floor":[("sensor.aqara_floor",aqara)],
            "radiator":[("sensor.supla_radiator",supla)]}

def test_normal_aqara_supla():
    assert validate_sample(raw())["valid"]

def test_aqara_unknown():
    result=validate_sample(raw(aqara="unknown"))
    assert not result["valid"]
    assert any("unavailable" in x for x in result["errors"])

def test_supla_unavailable():
    result=validate_sample(raw(supla="unavailable"))
    assert not result["valid"]

def test_missing_sensor_state():
    result=validate_sample(raw(aqara=None))
    assert not result["valid"]

def test_non_numeric_payload():
    result=validate_sample(raw(supla="error"))
    assert not result["valid"]
    assert any("non-numeric" in x for x in result["errors"])

def test_impossible_temperature():
    result=validate_sample(raw(aqara="99"))
    assert not result["valid"]
    assert any("outside safe range" in x for x in result["errors"])

def test_recovery_after_failure():
    failed=validate_sample(raw(aqara="unavailable"))
    recovered=validate_sample(raw(aqara="21.9"))
    assert not failed["valid"]
    assert recovered["valid"]

def test_invalid_sample_cannot_create_recommendation():
    valid=[validate_sample(raw()) for _ in range(3)]
    invalid=validate_sample(raw(supla="unavailable"))
    result=analyze(valid+[invalid], expected_samples=24)
    assert result["status"]=="insufficient_data"
    assert "adjustment" not in result
