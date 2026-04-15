"""The MyAir3 integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MyAir3Api
from .const import CONF_HOST, CONF_PORT, DEFAULT_PORT
from .coordinator import MyAir3DataCoordinator, MyAir3DataConfigEntry

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(
    hass: HomeAssistant, entry: MyAir3DataConfigEntry
) -> bool:
    """Set up MyAir3 from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)

    api = MyAir3Api(host, port, async_get_clientsession(hass))
    coordinator = MyAir3DataCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: MyAir3DataConfigEntry
) -> bool:
    """Unload a MyAir3 config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
