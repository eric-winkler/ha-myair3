"""Climate platform for the MyAir3 integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import PRECISION_WHOLE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    MYAIR3_FAN_HIGH,
    MYAIR3_FAN_LOW,
    MYAIR3_FAN_MEDIUM,
    MYAIR3_MODE_COOL,
    MYAIR3_MODE_FAN_ONLY,
    MYAIR3_MODE_HEAT,
)
from .coordinator import MyAir3DataConfigEntry, MyAir3DataCoordinator
from .entity import MyAir3Entity

# Maps MyAir3 mode integers to HA HVAC modes
MYAIR3_TO_HA_MODE: dict[int, HVACMode] = {
    MYAIR3_MODE_COOL: HVACMode.COOL,
    MYAIR3_MODE_HEAT: HVACMode.HEAT,
    MYAIR3_MODE_FAN_ONLY: HVACMode.FAN_ONLY,
}
HA_TO_MYAIR3_MODE: dict[HVACMode, int] = {v: k for k, v in MYAIR3_TO_HA_MODE.items()}

# Maps MyAir3 fan speed integers to HA fan mode strings
MYAIR3_TO_HA_FAN: dict[int, str] = {
    MYAIR3_FAN_LOW: FAN_LOW,
    MYAIR3_FAN_MEDIUM: FAN_MEDIUM,
    MYAIR3_FAN_HIGH: FAN_HIGH,
}
HA_TO_MYAIR3_FAN: dict[str, int] = {v: k for k, v in MYAIR3_TO_HA_FAN.items()}

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyAir3DataConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the MyAir3 climate entity."""
    coordinator = config_entry.runtime_data
    async_add_entities([MyAir3Climate(coordinator)])


class MyAir3Climate(MyAir3Entity, ClimateEntity):
    """Climate entity representing the MyAir3 AC unit."""

    _attr_fan_modes = [FAN_LOW, FAN_MEDIUM, FAN_HIGH]
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT, HVACMode.FAN_ONLY]
    _attr_supported_features = (
        ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = PRECISION_WHOLE
    _attr_translation_key = "ac_unit"
    _attr_name = None

    def __init__(self, coordinator: MyAir3DataCoordinator) -> None:
        """Initialise the climate entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-climate"
        # Temp bounds come from the controller but set safe defaults until
        # the first coordinator update provides real values.
        self._attr_max_temp = 32
        self._attr_min_temp = 16

    @property
    def current_temperature(self) -> float | None:
        """Return the current measured temperature."""
        return self._system["central_actual_temp"]

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        return self._system["central_desired_temp"]

    @property
    def max_temp(self) -> float:
        """Return the maximum settable temperature from the controller."""
        return self._system.get("max_temp", 32)

    @property
    def min_temp(self) -> float:
        """Return the minimum settable temperature from the controller."""
        return self._system.get("min_temp", 16)

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current HVAC mode."""
        if not self._system["power"]:
            return HVACMode.OFF
        return MYAIR3_TO_HA_MODE.get(self._system["mode"], HVACMode.OFF)

    @property
    def fan_mode(self) -> str | None:
        """Return the current fan speed."""
        return MYAIR3_TO_HA_FAN.get(self._system["fan_speed"])

    async def async_turn_on(self) -> None:
        """Turn the AC on (preserving current mode and settings)."""
        system = self._system
        await self._async_call_api(
            self.coordinator.api.async_set_system_data(
                power=True,
                fan_speed=system["fan_speed"],
                mode=system["mode"],
                central_desired_temp=system["central_desired_temp"],
            )
        )

    async def async_turn_off(self) -> None:
        """Turn the AC off."""
        system = self._system
        await self._async_call_api(
            self.coordinator.api.async_set_system_data(
                power=False,
                fan_speed=system["fan_speed"],
                mode=system["mode"],
                central_desired_temp=system["central_desired_temp"],
            )
        )

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set a new HVAC mode."""
        system = self._system
        if hvac_mode == HVACMode.OFF:
            await self.async_turn_off()
            return
        await self._async_call_api(
            self.coordinator.api.async_set_system_data(
                power=True,
                fan_speed=system["fan_speed"],
                mode=HA_TO_MYAIR3_MODE[hvac_mode],
                central_desired_temp=system["central_desired_temp"],
            )
        )

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set a new fan speed."""
        system = self._system
        await self._async_call_api(
            self.coordinator.api.async_set_system_data(
                power=system["power"],
                fan_speed=HA_TO_MYAIR3_FAN[fan_mode],
                mode=system["mode"],
                central_desired_temp=system["central_desired_temp"],
            )
        )

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set the target temperature."""
        from homeassistant.const import ATTR_TEMPERATURE

        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        system = self._system
        await self._async_call_api(
            self.coordinator.api.async_set_system_data(
                power=system["power"],
                fan_speed=system["fan_speed"],
                mode=system["mode"],
                central_desired_temp=temp,
            )
        )
