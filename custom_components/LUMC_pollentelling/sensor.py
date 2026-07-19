"""Sensor platform for LUMC Pollentelling."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_CACHE_TTL, DOMAIN
from .html_scraper import extract_pollen_values, fetch_html

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    cache_ttl = entry.data[CONF_CACHE_TTL]

    html = await hass.async_add_executor_job(fetch_html)
    if not html:
        _LOGGER.error("Initial HTML fetch failed; no sensors created")
        return

    pollen_values = await hass.async_add_executor_job(extract_pollen_values, html)
    if not pollen_values:
        _LOGGER.error("No pollen values found; no sensors created")
        return

    sensors = [
        LumcPollenSensor(entry.entry_id, pollen_name, cache_ttl)
        for pollen_name in pollen_values
    ]

    _LOGGER.debug("Creating sensors for pollen types: %s", list(pollen_values))
    async_add_entities(sensors, update_before_add=True)


class LumcPollenSensor(SensorEntity):
    """LUMC Pollen Sensor class."""

    _attr_icon = "mdi:flower-pollen"

    def __init__(self, entry_id: str, pollen_name: str, cache_ttl: int) -> None:
        """Initialize the sensor class."""
        self._entry_id = entry_id
        self._pollen_name = pollen_name
        self._cache_ttl = timedelta(seconds=cache_ttl)
        self._last_update: datetime | None = None
        self._state: int | None = None

        safe_name = pollen_name.lower().replace(" ", "_")
        self._attr_unique_id = f"{entry_id}_{safe_name}"
        self._attr_name = pollen_name
        self._attr_entity_registry_enabled_default = pollen_name in {
            "Grassen",
            "Els",
            "Grassen-familie",
        }
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            manufacturer="madcowGit",
            model="LUMC Pollentelling",
            name="LUMC Pollentelling",
        )

    @property
    def native_value(self) -> int | None:
        """Return the native value of the sensor."""
        return self._state

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        now = datetime.now(tz=UTC)

        if self._last_update and now - self._last_update < self._cache_ttl:
            return

        html = await self.hass.async_add_executor_job(fetch_html)
        if not html:
            _LOGGER.warning("HTML fetch failed during update")
            return

        pollen_values = await self.hass.async_add_executor_job(
            extract_pollen_values, html
        )

        if self._pollen_name in pollen_values:
            value = pollen_values[self._pollen_name]
            _LOGGER.debug("Updating %s -> %s", self._pollen_name, value)
            self._state = value
            self._last_update = now
        else:
            _LOGGER.warning(
                "Pollen type '%s' missing in latest HTML", self._pollen_name
            )
