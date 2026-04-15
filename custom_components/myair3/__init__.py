"""The MyAir3 integration."""
from __future__ import annotations

from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MyAir3ApiClient
from .const import DOMAIN, PLATFORMS
from .coordinator import MyAir3ConfigEntry, MyAir3Coordinator


async def async_setup_entry(hass: HomeAssistant, entry: MyAir3ConfigEntry) -> bool:
    """Set up MyAir3 from a config entry."""
    ip = entry.data[CONF_IP_ADDRESS]
    session = async_get_clientsession(hass)
    client = MyAir3ApiClient(ip, session)
    coordinator = MyAir3Coordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: MyAir3ConfigEntry) -> bool:
    """Unload a MyAir3 config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
