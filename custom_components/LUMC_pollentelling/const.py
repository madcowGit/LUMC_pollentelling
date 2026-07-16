"""Constants for LUMC Pollentelling."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "LUMC_pollentelling"
CONF_CACHE_TTL = "cache_ttl"
DEFAULT_CACHE_TTL = 3600

