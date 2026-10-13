"""Bootstrap pure logic tests before pytest imports test modules.

Importing the HA integration __init__.py requires a running Home Assistant.
Only dependency-free modules are loaded here; lifecycle tests supply HA fakes.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "custom_components.heat_curve_optimizer"

for name, path in [
    ("custom_components", ROOT / "custom_components"),
    (PACKAGE, ROOT / "custom_components" / "heat_curve_optimizer"),
]:
    if name not in sys.modules:
        module = types.ModuleType(name)
        module.__path__ = [str(path)]
        sys.modules[name] = module

for name in ("const", "validation", "algorithm"):
    fullname = f"{PACKAGE}.{name}"
    if fullname not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            fullname,
            ROOT / "custom_components" / "heat_curve_optimizer" / f"{name}.py",
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[fullname] = module
        spec.loader.exec_module(module)
