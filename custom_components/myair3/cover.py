"""Cover platform for MyAir3 — zone damper control."""
from __future__ import annotations

from typing import Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import MyAir3ConfigEntry, MyAir3Coordinator
from .entity import MyAir3ZoneEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyAir3ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MyAir3 cover platform."""
    coordinator = config_entry.runtime_data
    async_add_entities(
        MyAir3ZoneDamper(coordinator, zone_id)
        for zone_id in coordinator.data["zones"]
    )


class MyAir3ZoneDamper(MyAir3ZoneEntity, CoverEntity):
    """Damper cover for a MyAir3 zone."""

    _attr_device_class = CoverDeviceClass.DAMPER
    _attr_name = "Damper"
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_POSITION
    )

    def __init__(self, coordinator: MyAir3Coordinator, zone_id: int) -> None:
        """Initialize the damper cover."""
        super().__init__(coordinator, zone_id)
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_zone_{zone_id}_damper"
        )

    @property
    def current_cover_position(self) -> int:
        """Return the current damper position as a percentage 0–100."""
        return self.coordinator.data["zones"][self.zone_id]["damper_percent"]

    @property
    def is_closed(self) -> bool:
        """Return True if the damper is fully closed."""
        return self.coordinator.data["zones"][self.zone_id]["damper_percent"] == 0

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Fully open the damper."""
        await self._set_damper(100)

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Fully close the damper."""
        await self._set_damper(0)

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the damper to a specific position."""
        await self._set_damper(kwargs[ATTR_POSITION])

    async def _set_damper(self, percent: int) -> None:
        """Round to nearest 10 (half-up), send to API, and optimistically update state."""
        rounded = int((percent + 5) // 10) * 10
        zone = self.coordinator.data["zones"][self.zone_id]
        await self.coordinator.client.set_zone_data(
            zone_number=self.zone_id,
            enabled=rounded > 0,
            damper_percent=rounded,
            name=zone["name"],
        )
        self.coordinator.data["zones"][self.zone_id]["damper_percent"] = rounded
        self.coordinator.data["zones"][self.zone_id]["enabled"] = rounded > 0
        self.async_write_ha_state()
