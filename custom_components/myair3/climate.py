"""Climate platform for MyAir3."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, CONF_IP_ADDRESS, PRECISION_WHOLE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    FAN_MODE_TO_MYAIR3,
    HVAC_MODE_TO_MYAIR3,
    MYAIR3_TO_FAN_MODE,
    MYAIR3_TO_HVAC_MODE,
)
from .coordinator import MyAir3ConfigEntry, MyAir3Coordinator
from .entity import MyAir3Entity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyAir3ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MyAir3 climate platform."""
    coordinator = config_entry.runtime_data
    async_add_entities([MyAir3SystemClimate(coordinator, config_entry)])


class MyAir3SystemClimate(MyAir3Entity, ClimateEntity):
    """Climate entity for the MyAir3 system."""

    _attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT, HVACMode.FAN_ONLY]
    _attr_fan_modes = ["low", "medium", "high"]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = PRECISION_WHOLE
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_name = None

    def __init__(self, coordinator: MyAir3Coordinator, config_entry: MyAir3ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = config_entry.data[CONF_IP_ADDRESS]

    @property
    def unitcontrol(self):
        return self.coordinator.data["unitcontrol"]

    @property
    def current_temperature(self) -> float | None:
        return self.unitcontrol["central_actual_temp"]

    @property
    def target_temperature(self) -> float | None:
        return self.unitcontrol["central_desired_temp"]

    @property
    def min_temp(self) -> float:
        return self.unitcontrol["min_temp"]

    @property
    def max_temp(self) -> float:
        return self.unitcontrol["max_temp"]

    @property
    def hvac_mode(self) -> HVACMode:
        if not self.unitcontrol["power_on"]:
            return HVACMode.OFF
        return MYAIR3_TO_HVAC_MODE.get(self.unitcontrol["mode"], HVACMode.OFF)

    @property
    def fan_mode(self) -> str | None:
        return MYAIR3_TO_FAN_MODE.get(self.unitcontrol["fan_speed"])

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.client.set_system_data(airconOnOff=0)
        else:
            mode = HVAC_MODE_TO_MYAIR3[hvac_mode]
            await self.coordinator.client.set_system_data(airconOnOff=1, mode=mode)
        await self.coordinator.async_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        fan_speed = FAN_MODE_TO_MYAIR3[fan_mode]
        await self.coordinator.client.set_system_data(fanSpeed=fan_speed)
        await self.coordinator.async_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if temp := kwargs.get(ATTR_TEMPERATURE):
            await self.coordinator.client.set_system_data(centralDesiredTemp=temp)
            await self.coordinator.async_refresh()

    async def async_turn_on(self) -> None:
        await self.coordinator.client.set_system_data(airconOnOff=1)
        await self.coordinator.async_refresh()

    async def async_turn_off(self) -> None:
        await self.coordinator.client.set_system_data(airconOnOff=0)
        await self.coordinator.async_refresh()
