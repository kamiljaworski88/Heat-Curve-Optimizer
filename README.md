# Heat Curve Optimizer

**Heat Curve Optimizer** is a Home Assistant custom integration that learns how a house reacts to outdoor temperature and provides conservative, read-only heating-curve advice. It is designed for mixed installations such as **underfloor heating + radiators sharing one supply temperature**.

> The integration is an advisor. It does **not** automatically change heat-pump settings.

## Highlights — v0.9.1

- separate analysis of underfloor-heating and radiator zones with one safe shared-supply decision;
- per-room diagnostics that can identify an isolated cold/hot room instead of incorrectly changing the whole curve;
- optional supply/return analysis with ΔT diagnostics;
- optional thermostat/valve-state gating;
- learned house profile in outdoor-temperature bands;
- advisory distinction between likely **curve offset** and **curve slope** problems;
- explicit **I applied the recommendation** button for evaluating real changes;
- **FastMile Dashboard v2** — bundled responsive JavaScript card with navigation, gauges and SVG visualization;
- local data storage and a Data collection switch.

## Installation through HACS

1. Back up Home Assistant.
2. Open **HACS → Custom repositories**.
3. Add the repository as **Integration**:
   `https://github.com/kamiljaworski88/Heat-Curve-Optimizer`
4. Install/update **Heat Curve Optimizer**.
5. Restart Home Assistant.
6. Go to **Settings → Devices & services → Add integration → Heat Curve Optimizer**.
7. Select outdoor temperature, target temperature and at least one room-temperature entity.
8. Optionally configure supply, return and thermostat/valve entities.
9. Enable **Data collection** when the heating system is operating.

### FastMile JavaScript dashboard — no manual file copy

From **v0.9.1**, the FastMile card is bundled inside the integration. The integration exposes the JavaScript file itself and attempts to register it automatically as a Lovelace module. You no longer need to copy the file to `/config/www`.

After installing/updating and restarting Home Assistant, add a **Manual card** to a dashboard:

```yaml
type: custom:heat-curve-fastmile-card
applied_button: button.i_applied_the_recommendation
```

If Home Assistant uses a different entity ID for the confirmation button, replace `button.i_applied_the_recommendation` with the actual ID from **Developer Tools → States**.

The bundled resource is served at:

```text
/heat_curve_optimizer/heat-curve-fastmile-card.js
```

If your Home Assistant installation uses YAML-managed Lovelace resources, automatic resource registration may not be available. In that case add the URL above as a JavaScript module in your YAML resource configuration.

## Dashboard variants

- **FastMile Dashboard v2:** [dashboard/heat_curve_fastmile.yaml](dashboard/heat_curve_fastmile.yaml) — recommended custom JavaScript UI.
- **Full native Lovelace dashboard:** [dashboard/heat_curve_optimizer.yaml](dashboard/heat_curve_optimizer.yaml).
- **Compact native widget:** [dashboard/heat_curve_optimizer_widget.yaml](dashboard/heat_curve_optimizer_widget.yaml).

### FastMile Dashboard v2

The JavaScript card provides internal navigation for:

- **Overview** — system status, recommendation, coverage/confidence and temperature visualization;
- **Rooms** — room-level diagnostics;
- **House learning** — learned response time, outdoor-temperature profile and slope/offset conclusion;
- **Installation** — supply, return and ΔT diagnostics.

It is responsive and intended especially for wall/tablet dashboards while remaining usable on phones.

## Decision and learning model

Heat Curve Optimizer assumes one shared supply temperature for the configured heating zones. It therefore avoids averaging contradictory demands into a misleading recommendation.

A materially underheated zone has priority when the other zone is within its comfort deadband. Lowering is allowed only when no zone is underheated. Simultaneous meaningful underheating and overheating results in a conflict instead of a shared-curve change.

From v0.6 onward, room-level analysis can classify a single room as a local issue and advise checking its valve, thermostat or flow before changing the whole heating curve. Supply/return data can provide observational ΔT diagnostics. Configured thermostat/valve states can block unsafe conclusions when rooms are being throttled.

The learned outdoor-temperature profile is used to distinguish patterns that are more consistent with **offset** or **slope** adjustment. These remain recommendations, not automatic control.

## Data collection and learning

The integration starts with data collection disabled. Enable it when central heating is genuinely operating.

Learning includes:

- compact recommendation history;
- building response-time estimation;
- 5 °C outdoor-temperature profile bands;
- post-change evaluation after an explicitly confirmed change;
- comparable-weather safeguards.

The **I applied the recommendation** button tells the integration that the current recommendation was actually implemented. It does not modify the heat pump.

## Tests

The GitHub Actions workflow runs Python compilation, pytest and manifest checks. Unit tests use mocked Home Assistant/Aqara/Supla-style states rather than physical equipment. A green CI result does not replace testing after restart on a real Home Assistant instance.

## Safety and privacy

- no automatic heat-pump control;
- no cloud service required by this integration;
- samples are stored locally in Home Assistant;
- do not publish tokens, household entity IDs or `.storage` contents;
- hydraulic diagnostics are observational and do not replace commissioning measurements;
- slope/offset conclusions require sufficient data across different outdoor conditions.

## Documentation

- **Polska instrukcja:** [docs/INSTRUKCJA_PL.md](docs/INSTRUKCJA_PL.md)
- **FastMile card example:** [dashboard/heat_curve_fastmile.yaml](dashboard/heat_curve_fastmile.yaml)
- **Full dashboard:** [dashboard/heat_curve_optimizer.yaml](dashboard/heat_curve_optimizer.yaml)
- **Compact widget:** [dashboard/heat_curve_optimizer_widget.yaml](dashboard/heat_curve_optimizer_widget.yaml)

## Current limitations

Sensor update age/frozen-state detection is still limited. House-learning quality depends on having meaningful heating operation across sufficiently different outdoor conditions. Local thermostats, hydraulic balancing and other heat sources can affect observed temperatures, so the integration deliberately blocks or softens advice when configured control-state information indicates that the data may be misleading.
