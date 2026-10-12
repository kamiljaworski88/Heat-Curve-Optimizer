from custom_components.heat_curve_optimizer.validation import validate_sample

def test_aqara_and_supla_valid():
    s=validate_sample({"outdoor":"4.8","target":"22","floor":[("sensor.aqara_salon","21.8")],
                       "radiator":[("sensor.supla_bedroom","20.9")]})
    assert s["valid"]
    assert s["floor"] == [21.8]
    assert s["radiator"] == [20.9]

def test_unavailable_sensor_blocks_sample():
    s=validate_sample({"outdoor":"4","target":"22","floor":[("sensor.aqara_salon","unavailable")],"radiator":[]})
    assert not s["valid"]
    assert any("unavailable" in e for e in s["errors"])

def test_out_of_range_blocks_sample():
    s=validate_sample({"outdoor":"150","target":"22","floor":[("sensor.aqara_salon","21")],"radiator":[]})
    assert not s["valid"]
    assert any("outside safe range" in e for e in s["errors"])
