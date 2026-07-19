"""Camera platform for LUMC Pollentelling."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_CACHE_TTL, DOMAIN
from .lumc_client import LUMCPollenClient, PollenNotFound

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the camera platform."""
    cache_ttl = entry.data[CONF_CACHE_TTL]
    client = LUMCPollenClient(ttl_seconds=cache_ttl)

    names = await hass.async_add_executor_job(client.list_names)
    if not names:
        _LOGGER.error("No pollen names found; no camera entities created")
        return

    cameras = [
        LumcPollenHistoryCamera(entry.entry_id, pollen_name, cache_ttl, client)
        for pollen_name in names
    ]

    async_add_entities(cameras, True)


class LumcPollenHistoryCamera(Camera):
    """LUMC Pollen history camera entity."""

    _attr_icon = "mdi:flower"
    _attr_device_class = None
    _attr_should_poll = True

    def __init__(
        self,
        entry_id: str,
        pollen_name: str,
        cache_ttl: int,
        client: LUMCPollenClient,
    ) -> None:
        """Initialize the camera entity."""
        super().__init__()
        self._pollen_name = pollen_name
        self._client = client
        self._cache_ttl = timedelta(seconds=cache_ttl)
        self._last_update: datetime | None = None
        self._image: bytes | None = None

        safe_name = pollen_name.lower().replace(" ", "_")
        self._attr_unique_id = f"{entry_id}_{safe_name}_history_graph"
        self._attr_name = f"{pollen_name} History Graph"
        self._attr_entity_registry_enabled_default = pollen_name in {
            "Els",
            "Grassen-familie",
        }
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            manufacturer="LUMC",
            model="Pollentelling",
            name="LUMC Pollentelling",
        )
        self.content_type = "image/png"

    async def async_update(self) -> None:
        """Update the cached graph image."""
        now = datetime.utcnow()
        if self._last_update and now - self._last_update < self._cache_ttl:
            return

        try:
            image = await self.hass.async_add_executor_job(
                self._client.get_history_graph_png, self._pollen_name
            )
        except PollenNotFound:
            _LOGGER.warning(
                "History graph not found for pollen type '%s'", self._pollen_name
            )
            self._image = None
            return
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error(
                "Error fetching history graph for '%s': %s",
                self._pollen_name,
                err,
            )
            self._image = None
            return

        self._image = image
        self._last_update = now

    async def async_camera_image(
        self,
        width: int | None = None,
        height: int | None = None,
    ) -> bytes | None:
        """Return image bytes for the camera."""
        if not self._image or (
            self._last_update
            and datetime.utcnow() - self._last_update >= self._cache_ttl
        ):
            await self.async_update()
        return self._image
