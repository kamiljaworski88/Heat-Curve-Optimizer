from custom_components.heat_curve_optimizer.algorithm import analyze


def samples(room=21.0, target=22.0, count=24, floor=22.0, outdoor=2.0):
    return [
        {
            "valid": True,
            "outdoor": outdoor,
            "target": target,
            "floor": [floor],
            "radiator": [room],
        }
        for _ in range(count)
    ]


def test_materially_conflicting_zones_block_recommendation():
    result = analyze(samples(room=21.0, floor=23.0), 24)
    assert result["status"] == "zone_conflict"
    assert "adjustment" not in result
    assert result["zones"]["floor"]["error"] == -1.0
    assert result["zones"]["radiator"]["error"] == 1.0
    assert "one supply temperature" in result["reason"]


def test_underheated_radiators_have_priority_over_floor_in_deadband():
    result = analyze(samples(room=21.2, floor=22.2), 24)
    assert result["status"] == "ready"
    assert result["adjustment"] == 1.0
    assert result["governing_zone"] == "radiator"
    assert result["decision_basis"] == "shared_supply"


def test_underheated_floor_has_priority_over_radiators_in_deadband():
    result = analyze(samples(room=22.2, floor=21.2), 24)
    assert result["status"] == "ready"
    assert result["adjustment"] == 1.0
    assert result["governing_zone"] == "floor"


def test_both_zones_cold_raise_from_coldest_zone():
    result = analyze(samples(room=21.0, floor=21.1), 24)
    assert result["status"] == "ready"
    assert result["adjustment"] == 2.0
    assert result["governing_zone"] == "radiator"


def test_lower_only_when_no_zone_is_underheated():
    result = analyze(samples(room=22.7, floor=22.5), 24)
    assert result["status"] == "ready"
    assert result["adjustment"] == -1.0
    assert result["governing_zone"] == "radiator"


def test_deadband_no_change():
    result = analyze(samples(room=21.8, floor=22.1), 24)
    assert result["status"] == "ready"
    assert result["adjustment"] == 0.0
    assert result["governing_zone"] is None


def test_insufficient_data_has_no_recommendation():
    result = analyze(samples(count=5), 24)
    assert result["status"] == "insufficient_data"
    assert "adjustment" not in result


def test_unstable_outdoor_conditions_block_recommendation():
    data = samples(count=24)
    for index, sample in enumerate(data):
        sample["outdoor"] = -5.0 if index % 2 == 0 else 5.0
    result = analyze(data, 24)
    assert result["status"] == "unstable_conditions"
    assert "adjustment" not in result
    assert result["outdoor_stddev"] > 3.0


def test_weather_context_is_exposed():
    result = analyze(samples(outdoor=3.5), 24)
    assert result["outdoor_average"] == 3.5
    assert result["outdoor_min"] == 3.5
    assert result["outdoor_max"] == 3.5
    assert result["outdoor_stddev"] == 0.0
