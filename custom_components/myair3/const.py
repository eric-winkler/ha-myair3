"""Constants for MyAir3."""
from homeassistant.components.climate import HVACMode
from homeassistant.const import Platform

DOMAIN = "myair3"
PLATFORMS = [Platform.CLIMATE, Platform.SENSOR]

HVAC_MODE_TO_MYAIR3 = {
    HVACMode.COOL: 1,
    HVACMode.HEAT: 2,
    HVACMode.FAN_ONLY: 3,
}
MYAIR3_TO_HVAC_MODE = {v: k for k, v in HVAC_MODE_TO_MYAIR3.items()}

FAN_MODE_TO_MYAIR3 = {"low": 1, "medium": 2, "high": 3}
MYAIR3_TO_FAN_MODE = {v: k for k, v in FAN_MODE_TO_MYAIR3.items()}

UPDATE_INTERVAL_SECONDS = 15
DEFAULT_TIMEOUT = 10
