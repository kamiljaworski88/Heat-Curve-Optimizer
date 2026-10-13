from custom_components.heat_curve_optimizer.coordinator import HeatCurveOptimizerCoordinator


def test_paused_result_is_safe():
    coordinator = object.__new__(HeatCurveOptimizerCoordinator)
    result = coordinator._paused_result()
    assert result["status"] == "paused"
    assert result["coverage"] == 0.0
    assert result["confidence"] == 0.0
    assert result["data_quality"] == "paused"
    assert "adjustment" not in result
