"""Zone disagreement must never trigger an automatic recommendation."""
from custom_components.heat_curve_optimizer.algorithm import analyze

def samples(floor, radiator, count=24):
    return [{"valid": True, "outdoor": 2.0, "target": 22.0,
             "floor": [floor], "radiator": [radiator]} for _ in range(count)]

def test_floor_satisfied_radiator_cold_is_conflict():
    result = analyze(samples(22.0, 21.0), 24)
    assert result["status"] == "zone_conflict"
    assert "adjustment" not in result

def test_both_zones_cold_can_suggest_offset():
    result = analyze(samples(21.0, 21.1), 24)
    assert result["status"] == "ready"
    assert result["adjustment"] == 2.0

def test_missing_samples_suppress_recommendation():
    result = analyze(samples(21.0, 21.0, 3), 24)
    assert result["status"] == "insufficient_data"
    assert "adjustment" not in result
