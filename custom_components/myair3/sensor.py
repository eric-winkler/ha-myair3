"""Sensor platform for MyAir3."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import MyAir3ConfigEntry, MyAir3Coordinator
from .entity import MyAir3Entity, MyAir3ZoneEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyAir3ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MyAir3 sensor platform."""
    coordinator = config_entry.runtime_data
    entities: list[SensorEntity] = [MyAir3SystemTempSensor(coordinator)]
    for zone_id in coordinator.data["zones"]:
        entities.append(MyAir3ZoneDamperSensor(coordinator, zone_id))
    async_add_entities(entities)


class MyAir3SystemTempSensor(MyAir3Entity, SensorEntity):
    """Temperature sensor for the MyAir3 system."""

    _attr_name = "Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: MyAir3Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_temperature"

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data["unitcontrol"]["central_actual_temp"]


class MyAir3ZoneDamperSensor(MyAir3ZoneEntity, SensorEntity):
    """Damper position sensor for a MyAir3 zone."""

    _attr_name = "Damper"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:valve"

    def __init__(self, coordinator: MyAir3Coordinator, zone_id: int) -> None:
        super().__init__(coordinator, zone_id)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_zone_{zone_id}_damper"

    @property
    def native_value(self) -> int | None:
        return self.coordinator.data["zones"][self.zone_id]["damper_percent"]
