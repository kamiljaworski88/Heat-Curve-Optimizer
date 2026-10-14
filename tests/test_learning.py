from custom_components.heat_curve_optimizer.learning import (
    build_house_profile, estimate_response_hours, evaluate_change, new_change,
    outdoor_bucket, recommendation_snapshot,
)

def snap(ts, error, outdoor=2.0, adjustment=1.0, confidence=.8):
    return {"timestamp": ts, "error": error, "outdoor": outdoor, "adjustment": adjustment, "confidence": confidence}

def test_outdoor_bucket():
    assert outdoor_bucket(2.1) == "+0..+5C"
    assert outdoor_bucket(-1.0) == "-5..+0C"

def test_house_profile_requires_repeated_observations():
    history = [snap("2026-01-01T00:00:00+00:00", .5), snap("2026-01-01T06:00:00+00:00", .3)]
    assert build_house_profile(history) == {}
    history.append(snap("2026-01-01T12:00:00+00:00", .1))
    profile = build_house_profile(history)
    assert profile["+0..+5C"]["observations"] == 3
    assert profile["+0..+5C"]["average_error"] == .3

def test_response_time_uses_comparable_weather():
    history = [
        snap("2026-01-01T00:00:00+00:00", 1.0, 2.0),
        snap("2026-01-01T03:00:00+00:00", .9, 8.0),
        snap("2026-01-01T06:00:00+00:00", .7, 2.5),
        snap("2026-01-01T12:00:00+00:00", .6, 2.0),
    ]
    assert estimate_response_hours(history) == 6.0

def test_change_evaluation_waits_then_scores_improvement():
    change = {"timestamp":"2026-01-01T00:00:00+00:00","baseline_error":1.0,"outdoor":2.0,"adjustment":1.0}
    early = [snap("2026-01-01T06:00:00+00:00", .5)]
    assert evaluate_change(change, early)["status"] == "waiting"
    later = early + [snap("2026-01-01T12:00:00+00:00", .6, 2.5)]
    result = evaluate_change(change, later)
    assert result["status"] == "improved"
    assert result["improvement"] == .4

def test_snapshot_only_for_ready_result():
    assert recommendation_snapshot({"status":"zone_conflict"}, "x") is None
    result = recommendation_snapshot({"status":"ready","adjustment":1,"error":.5,"outdoor_average":2,"confidence":.8}, "x")
    assert result["adjustment"] == 1.0

def test_new_change_is_explicit_record():
    change = new_change(-1, {"error":-.7,"outdoor_average":3.0}, "2026-01-01T00:00:00+00:00")
    assert change["adjustment"] == -1.0
    assert change["baseline_error"] == -.7
