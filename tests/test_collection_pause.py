"""Collection pause / resume, migration and restart regression tests."""
import asyncio
from datetime import datetime, timezone
from test_coordinator_lifecycle import _coordinator_class, _states


def test_pause_does_not_collect_and_resumes(monkeypatch):
    klass, hass, entry = _coordinator_class(monkeypatch, None, _states())
    coordinator = klass(hass, entry)
    asyncio.run(coordinator.async_initialize())
    assert coordinator.result["status"] == "paused"
    assert coordinator.samples == []
    asyncio.run(coordinator._scheduled_collect(None))
    assert coordinator.samples == []
    asyncio.run(coordinator.async_set_collection_enabled(True))
    assert len(coordinator.samples) == 1
    assert coordinator.collection_enabled
    asyncio.run(coordinator.async_set_collection_enabled(False))
    assert coordinator.result["status"] == "paused"
    assert coordinator.result["coverage"] == 0
    assert "adjustment" not in coordinator.result
    asyncio.run(coordinator._scheduled_collect(None))
    assert len(coordinator.samples) == 1
    asyncio.run(coordinator.async_shutdown())


def test_v2_restart_restores_switch_and_history(monkeypatch):
    sample = {"timestamp": datetime.now(timezone.utc).isoformat(),
              "valid": True, "outdoor": 3.0, "target": 22.0,
              "floor": [21.4], "radiator": [21.5]}
    klass, hass, entry = _coordinator_class(monkeypatch, {
        "schema_version": 2, "collection_enabled": False, "samples": [sample]
    }, _states())
    coordinator = klass(hass, entry)
    asyncio.run(coordinator.async_initialize())
    assert coordinator.result["status"] == "paused"
    assert coordinator.samples == [sample]
    assert not coordinator.collection_enabled
    asyncio.run(coordinator.async_shutdown())


def test_legacy_samples_are_discarded_once(monkeypatch):
    klass, hass, entry = _coordinator_class(monkeypatch, {
        "samples": [{"timestamp": datetime.now(timezone.utc).isoformat(), "valid": True}]
    }, _states())
    coordinator = klass(hass, entry)
    asyncio.run(coordinator.async_initialize())
    assert coordinator.samples == []
    assert coordinator.result["status"] == "paused"
    asyncio.run(coordinator.async_shutdown())
