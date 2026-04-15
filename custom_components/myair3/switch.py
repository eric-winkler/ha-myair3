"""Switch platform for the MyAir3 integration – zone enable/disable."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import MyAir3DataConfigEntry, MyAir3DataCoordinator
from .entity import MyAir3ZoneEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyAir3DataConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up MyAir3 zone switches."""
    coordinator = config_entry.runtime_data
    async_add_entities(
        MyAir3ZoneSwitch(coordinator, zone_num)
        for zone_num in coordinator.data["zones"]
    )


class MyAir3ZoneSwitch(MyAir3ZoneEntity, SwitchEntity):
    """Switch entity that enables or disables a single zone."""

    _attr_translation_key = "zone"

    def __init__(self, coordinator: MyAir3DataCoordinator, zone_num: int) -> None:
        """Initialise the zone switch."""
        super().__init__(coordinator, zone_num)
        self._attr_name = self._zone["name"]

    @property
    def is_on(self) -> bool:
        """Return True when the zone is enabled."""
        return self._zone["enabled"]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable the zone."""
        zone = self._zone
        await self._async_call_api(
            self.coordinator.api.async_set_zone_data(
                zone_num=self.zone_num,
                enabled=True,
                name=zone["name"],
                user_percent=zone["user_percent"],
            )
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable the zone."""
        zone = self._zone
        await self._async_call_api(
            self.coordinator.api.async_set_zone_data(
                zone_num=self.zone_num,
                enabled=False,
                name=zone["name"],
                user_percent=zone["user_percent"],
            )
        )
