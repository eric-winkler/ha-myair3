"""Sensor platform for the MyAir3 integration – temperature readings."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import MyAir3DataConfigEntry, MyAir3DataCoordinator
from .entity import MyAir3Entity, MyAir3ZoneEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyAir3DataConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up MyAir3 sensor entities."""
    coordinator = config_entry.runtime_data
    entities: list[SensorEntity] = [
        MyAir3CentralActualTempSensor(coordinator),
    ]
    for zone_num, zone in coordinator.data["zones"].items():
        entities.append(MyAir3ZoneActualTempSensor(coordinator, zone_num))
        if zone["has_climate_control"]:
            entities.append(MyAir3ZoneDesiredTempSensor(coordinator, zone_num))
    async_add_entities(entities)


class MyAir3CentralActualTempSensor(MyAir3Entity, SensorEntity):
    """Sensor reporting the central measured temperature of the AC unit."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_translation_key = "central_actual_temp"

    def __init__(self, coordinator: MyAir3DataCoordinator) -> None:
        """Initialise the central temperature sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}-central-actual-temp"
        )

    @property
    def native_value(self) -> float | None:
        """Return the current central temperature."""
        return self._system["central_actual_temp"]


class MyAir3ZoneActualTempSensor(MyAir3ZoneEntity, SensorEntity):
    """Sensor reporting the measured temperature in a zone."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_translation_key = "zone_actual_temp"

    def __init__(self, coordinator: MyAir3DataCoordinator, zone_num: int) -> None:
        """Initialise the zone temperature sensor."""
        super().__init__(coordinator, zone_num)
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}-zone{zone_num}-actual-temp"
        )
        self._attr_name = f"{self._zone['name']} Temperature"

    @property
    def native_value(self) -> float | None:
        """Return the zone's measured temperature."""
        return self._zone["actual_temp"]


class MyAir3ZoneDesiredTempSensor(MyAir3ZoneEntity, SensorEntity):
    """Sensor reporting the desired temperature set for a climate-controlled zone."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_translation_key = "zone_desired_temp"

    def __init__(self, coordinator: MyAir3DataCoordinator, zone_num: int) -> None:
        """Initialise the zone desired temperature sensor."""
        super().__init__(coordinator, zone_num)
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}-zone{zone_num}-desired-temp"
        )
        self._attr_name = f"{self._zone['name']} Target Temperature"

    @property
    def native_value(self) -> float | None:
        """Return the zone's desired temperature."""
        return self._zone["desired_temp"]
