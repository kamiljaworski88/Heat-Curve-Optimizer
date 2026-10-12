# Heat Curve Optimizer

Home Assistant custom integration (experimental, read-only). Select outdoor, target, floor-heating and radiator temperature sensors via UI. It collects samples, persists history and exposes recommendation, coverage, confidence, data-quality and diagnostic sensors.

## Install via HACS

HACS → Custom repositories → `https://github.com/kamiljaworski88/Heat-Curve-Optimizer` → Integration. Install, restart Home Assistant, then Settings → Devices & services → Add integration → Heat Curve Optimizer.

## Important safety limitations

**Experimental. Do not use recommendations as automatic heating control.** Current algorithm is heuristic, not a calibrated heating-curve slope model. Thermostatic valves, floor-loop actuators, room occupancy, weather changes, cooling by air conditioners and lack of heating-demand signals can make recommendations misleading. Check pump operation and hydraulic settings with your installer. No commands are sent to the heat pump.

## Privacy

No credentials, tokens, addresses or actual household entity IDs are committed. Selected entity IDs and sampled temperatures are stored only in Home Assistant local storage; do not publish your `.storage` files or diagnostic exports without review.

## Development

Run `pytest` with Home Assistant test dependencies available. Aqara/Supla simulations use mock states, not actual devices. A Home Assistant integration test and dashboard are still required before stable release.
