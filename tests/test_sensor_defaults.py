"""Tests for default sensor and camera behavior."""

# ruff: noqa: S101

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from custom_components.LUMC_pollentelling.camera import LumcPollenHistoryCamera
from custom_components.LUMC_pollentelling.const import DOMAIN
from custom_components.LUMC_pollentelling.sensor import LumcPollenSensor


def test_default_enable_state_for_known_pollen_types() -> None:
    """Known pollen types should be enabled by default."""
    for pollen_name in ("Grassen", "Els", "Grassen-familie"):
        sensor = LumcPollenSensor("entry-id", pollen_name, 3600)
        assert sensor.entity_registry_enabled_default is True

    for pollen_name in ("Berk", "Hout"):
        sensor = LumcPollenSensor("entry-id", pollen_name, 3600)
        assert sensor.entity_registry_enabled_default is False


def test_sensor_attaches_to_single_device() -> None:
    """Sensors should attach to a single device entry."""
    sensor = LumcPollenSensor("entry-id", "Grassen", 3600)

    assert sensor.device_info is not None
    assert sensor.device_info["identifiers"] == {(DOMAIN, "entry-id")}


def test_camera_is_enabled_by_default_and_attached_to_same_device() -> None:
    """Cameras should follow the same enablement and device rules."""
    for pollen_name in ("Els", "Grassen-familie"):
        camera = LumcPollenHistoryCamera("entry-id", pollen_name, 3600, None)
        assert camera.entity_registry_enabled_default is True

    camera = LumcPollenHistoryCamera("entry-id", "Grassen", 3600, None)
    assert camera.entity_registry_enabled_default is False
    assert camera.device_info is not None
    assert camera.device_info["identifiers"] == {(DOMAIN, "entry-id")}
