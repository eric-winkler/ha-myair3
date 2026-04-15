"""Base entity classes for the MyAir3 integration."""

from __future__ import annotations

from typing import Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import MyAir3ApiError
from .const import DOMAIN
from .coordinator import MyAir3DataCoordinator


class MyAir3Entity(CoordinatorEntity[MyAir3DataCoordinator]):
    """Base class for all MyAir3 entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: MyAir3DataCoordinator) -> None:
        """Initialise base entity."""
        super().__init__(coordinator)

        system = coordinator.data["system"]
        self._attr_unique_id: str = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            manufacturer="Advantage Air",
            model=f"MyAir3 (type {system['type']})",
            name=system["name"],
            sw_version=system["app_revision"],
        )

    @property
    def _system(self) -> dict[str, Any]:
        """Return the current system data."""
        return self.coordinator.data["system"]

    async def _async_call_api(self, coro) -> None:
        """Execute an API coroutine, translating errors to HA exceptions."""
        try:
            await coro
            await self.coordinator.async_request_refresh()
        except MyAir3ApiError as err:
            raise HomeAssistantError(str(err)) from err


class MyAir3ZoneEntity(MyAir3Entity):
    """Base class for entities that represent a single zone."""

    def __init__(self, coordinator: MyAir3DataCoordinator, zone_num: int) -> None:
        """Initialise zone entity."""
        super().__init__(coordinator)
        self.zone_num = zone_num
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-zone{zone_num}"

    @property
    def _zone(self) -> dict[str, Any]:
        """Return the current zone data."""
        return self.coordinator.data["zones"][self.zone_num]
