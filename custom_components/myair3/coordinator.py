"""Data update coordinator for the MyAir3 integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MyAir3Api, MyAir3ApiError
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

type MyAir3DataConfigEntry = ConfigEntry[MyAir3DataCoordinator]


class MyAir3DataCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls the MyAir3 controller for state updates."""

    config_entry: MyAir3DataConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: MyAir3DataConfigEntry,
        api: MyAir3Api,
    ) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest data from the controller."""
        try:
            return await self.api.async_get_data()
        except MyAir3ApiError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="update_failed",
                translation_placeholders={"error": str(err)},
            ) from err
