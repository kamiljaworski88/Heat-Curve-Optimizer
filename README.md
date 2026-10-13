# Heat Curve Optimizer

Experimental, **read-only** Home Assistant custom integration for conservative heating-curve recommendations. It separates underfloor heating from radiators and avoids recommendations when zones disagree or sensor data is invalid.

## Installation through HACS

1. Back up Home Assistant.
2. Open HACS → Custom repositories.
3. Add `https://github.com/kamiljaworski88/Heat-Curve-Optimizer` as **Integration**.
4. Install the integration, restart Home Assistant and go to Settings → Devices & services → Add integration → Heat Curve Optimizer.
5. Select outdoor and target temperature entities and at least one floor or radiator room temperature entity.
6. Turn on **Data collection** only when the heating system is actually running.
7. Allow a full analysis window to accumulate before acting on advice.

**Polska instrukcja:** [docs/INSTRUKCJA_PL.md](docs/INSTRUKCJA_PL.md)

**Dashboard:** [dashboard/heat_curve_optimizer.yaml](dashboard/heat_curve_optimizer.yaml) (Lovelace Sections template; adjust generated entity IDs and room sensors).

**Beta candidate notes:** [docs/RELEASE_NOTES_0.1.0-beta.md](docs/RELEASE_NOTES_0.1.0-beta.md). This document is not a published GitHub release.

## Tests

The workflow in `.github/workflows/tests.yml` runs `python -m pytest -q tests`, Python compilation and a manifest check. Tests use mock Aqara/Supla states and fake Home Assistant services, not physical devices or a full Home Assistant runtime. Check the actual Actions run result before installing the beta.

## Safety and privacy

No automatic heat-pump control. The current heuristic suggests a preliminary **offset**, not a calibrated slope. Thermostats, floor actuators, air conditioning, occupancy and pump heating mode are not modeled sufficiently for automatic decisions.

Never commit secrets, tokens, real household entity IDs or `.storage` files. Samples are stored locally in Home Assistant. Data collection can be paused from the integration switch; while paused, no samples are added and coverage does not increase. Existing valid history is preserved. Upgrading from the pre-switch storage schema discards the old uncontrolled sample history once and starts paused. Inspect diagnostics before sharing.

## Known limitations

- Optional supply/return, power and operation-state entities are selectable but not yet used for recommendations.
- Sensor update age is not yet checked; frozen but numeric states may be misleading.
- Room-specific targets and AC/thermostat demand signals are not modeled.
- HACS installation, actual restart and GitHub Actions green status must be verified before calling the release ready.
