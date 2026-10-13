from custom_components.heat_curve_optimizer.algorithm import analyze

def samples(room=21.0, target=22.0, count=24, floor=22.0):
    return [{"valid": True, "outdoor": 2.0, "target": target,
             "floor": [floor], "radiator": [room]} for _ in range(count)]

def test_conflicting_zones_block_recommendation():
    result = analyze(samples(21.0), 24)
    assert result["status"] == "zone_conflict"
    assert "adjustment" not in result
    assert result["zones"]["floor"]["error"] == 0.0
    assert result["zones"]["radiator"]["error"] == 1.0

def test_both_zones_cold():
    result = analyze(samples(21.0, floor=21.1), 24)
    assert result["status"] == "ready"
    assert result["adjustment"] == 2.0

def test_deadband_no_change():
    result = analyze(samples(21.8), 24)
    assert result["adjustment"] == 0.0

def test_insufficient_data_has_no_recommendation():
    result = analyze(samples(count=5), 24)
    assert result["status"] == "insufficient_data"
    assert "adjustment" not in result
