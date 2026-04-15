"""Binary sensor platform for the MyAir3 integration – zone diagnostic sensors."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
    """Set up MyAir3 binary sensor entities."""
    coordinator = config_entry.runtime_data
    entities: list[BinarySensorEntity] = []
    for zone_num in coordinator.data["zones"]:
        entities.append(MyAir3ZoneLowBatterySensor(coordinator, zone_num))
        entities.append(MyAir3ZoneMotorErrorSensor(coordinator, zone_num))
    async_add_entities(entities)


class MyAir3ZoneLowBatterySensor(MyAir3ZoneEntity, BinarySensorEntity):
    """Binary sensor indicating a low battery on a zone's wireless sensor."""

    _attr_device_class = BinarySensorDeviceClass.BATTERY
    _attr_translation_key = "zone_low_battery"

    def __init__(self, coordinator: MyAir3DataCoordinator, zone_num: int) -> None:
        """Initialise the low battery sensor."""
        super().__init__(coordinator, zone_num)
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}-zone{zone_num}-low-battery"
        )
        self._attr_name = f"{self._zone['name']} Low Battery"

    @property
    def is_on(self) -> bool:
        """Return True when the zone's sensor reports a low battery."""
        return self._zone["has_low_battery"]


class MyAir3ZoneMotorErrorSensor(MyAir3ZoneEntity, BinarySensorEntity):
    """Binary sensor indicating a motor error on a zone's damper."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_translation_key = "zone_motor_error"

    def __init__(self, coordinator: MyAir3DataCoordinator, zone_num: int) -> None:
        """Initialise the motor error sensor."""
        super().__init__(coordinator, zone_num)
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}-zone{zone_num}-motor-error"
        )
        self._attr_name = f"{self._zone['name']} Motor Error"

    @property
    def is_on(self) -> bool:
        """Return True when the zone's damper motor has an error."""
        return self._zone["has_motor_error"]
