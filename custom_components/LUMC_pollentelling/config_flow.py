"""Adds config flow for LUMC Pollentelling."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant import config_entries

if TYPE_CHECKING:
    from homeassistant.data_entry_flow import FlowResult

from .const import CONF_CACHE_TTL, DEFAULT_CACHE_TTL, DOMAIN
from .html_scraper import extract_pollen_values, fetch_html

_LOGGER = logging.getLogger(__name__)


class LumcPollenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for LUMC Pollentelling."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            return self.async_create_entry(
                title="LUMC pollentelling",
                data=user_input,
            )

        # Sanity check: can we at least see the table once?
        html = await self.hass.async_add_executor_job(fetch_html)
        if not html:
            return self.async_abort(reason="cannot_fetch_pollen_types")

        pollen_values = await self.hass.async_add_executor_job(
            extract_pollen_values, html
        )
        if not pollen_values:
            return self.async_abort(reason="cannot_fetch_pollen_types")

        schema = vol.Schema(
            {
                vol.Required(CONF_CACHE_TTL, default=DEFAULT_CACHE_TTL): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            description_placeholders={
                "documentation_url": "https://github.com/madcowGit/LUMC_pollentelling",
            },
        )
