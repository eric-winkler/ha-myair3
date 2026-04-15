"""Test configuration for MyAir3."""
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.const import CONF_IP_ADDRESS
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.myair3.const import DOMAIN

MOCK_IP = "192.168.1.100"
MOCK_SYSTEM_DATA = {
    "system": {"name": "Test Aircon", "type": 103, "my_app_rev": "2.0", "ip": MOCK_IP},
    "unitcontrol": {
        "power_on": True,
        "fan_speed": 2,
        "mode": 1,
        "central_actual_temp": 24.0,
        "central_desired_temp": 22.0,
        "min_temp": 16.0,
        "max_temp": 32.0,
        "number_of_zones": 2,
        "error_code": "0",
    },
    "zones": {
        1: {"name": "Living Room", "enabled": True, "damper_percent": 80},
        2: {"name": "Bedroom", "enabled": False, "damper_percent": 0},
    },
}


@pytest.fixture
def mock_config_entry():
    return MockConfigEntry(
        domain=DOMAIN,
        data={CONF_IP_ADDRESS: MOCK_IP},
        entry_id="test_entry_id",
    )


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.get_system_data = AsyncMock(return_value=MOCK_SYSTEM_DATA)
    client.set_system_data = AsyncMock()
    client.set_zone_data = AsyncMock()
    client.validate_connection = AsyncMock(return_value=True)
    return client
