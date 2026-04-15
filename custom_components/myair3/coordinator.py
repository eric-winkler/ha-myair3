"""DataUpdateCoordinator for MyAir3."""
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MyAir3ApiClient, MyAir3ApiError
from .const import DOMAIN, UPDATE_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)

type MyAir3ConfigEntry = ConfigEntry["MyAir3Coordinator"]


class MyAir3Coordinator(DataUpdateCoordinator):
    """Coordinator for MyAir3 data updates."""

    config_entry: MyAir3ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: MyAir3ConfigEntry,
        client: MyAir3ApiClient,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )
        self.client = client
        self.config_entry = entry

    async def _async_update_data(self):
        try:
            return await self.client.get_system_data()
        except MyAir3ApiError as err:
            raise UpdateFailed(
                f"Error communicating with MyAir3 API: {err}"
            ) from err
