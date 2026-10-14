from custom_components.heat_curve_optimizer.advanced import (
    room_diagnostics, hydraulic_diagnostics, thermostat_diagnostics, curve_shape_advice,
)

def test_isolated_cold_room_is_local_issue():
    samples=[{"rooms":{"radiator":[
        {"entity_id":"sensor.a","value":22.0},{"entity_id":"sensor.b","value":22.1},{"entity_id":"sensor.c","value":20.9}
    ],"floor":[]}} for _ in range(3)]
    r=room_diagnostics(samples,22.0)
    assert r["local_issue"]["type"]=="isolated_underheating"
    assert r["local_issue"]["entity_id"]=="sensor.c"

def test_multiple_cold_rooms_are_not_isolated():
    samples=[{"rooms":{"radiator":[
        {"entity_id":"sensor.a","value":21.0},{"entity_id":"sensor.b","value":21.1},{"entity_id":"sensor.c","value":22.0}
    ],"floor":[]}}]
    assert room_diagnostics(samples,22.0)["local_issue"] is None

def test_hydraulic_delta_t():
    r=hydraulic_diagnostics([{"supply":35,"return":30},{"supply":36,"return":31}])
    assert r["delta_t_average"]==5.0
    assert r["status"]=="ok"

def test_thermostats_can_block_curve_tuning():
    r=thermostat_diagnostics([{"thermostats":["off","closed","heat"]}])
    assert r["blocking"] is True

def test_profile_distinguishes_offset():
    p={"-5..+0C":{"observations":5,"average_error":.7},"+5..+10C":{"observations":5,"average_error":.6}}
    assert curve_shape_advice(p)["recommendation"]=="raise_offset"

def test_profile_distinguishes_slope():
    p={"-5..+0C":{"observations":5,"average_error":.8},"+5..+10C":{"observations":5,"average_error":.1}}
    assert curve_shape_advice(p)["recommendation"]=="increase_slope"

def test_profile_can_recommend_lower_slope():
    p={"-5..+0C":{"observations":5,"average_error":-.8},"+5..+10C":{"observations":5,"average_error":.1}}
    assert curve_shape_advice(p)["recommendation"]=="decrease_slope"
