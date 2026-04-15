"""Sensor platform for MyAir3."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import MyAir3ConfigEntry, MyAir3Coordinator
from .entity import MyAir3Entity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyAir3ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MyAir3 sensor platform."""
    coordinator = config_entry.runtime_data
    async_add_entities([MyAir3SystemTempSensor(coordinator)])


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
