"""Tests for MyAir3 sensor platform."""
from unittest.mock import patch

import pytest

from custom_components.myair3.const import DOMAIN



@pytest.fixture
async def setup_sensor(hass, mock_config_entry, mock_client, enable_custom_integrations):
    """Set up the sensor platform for testing."""
    with patch("custom_components.myair3.async_get_clientsession"), \
         patch("custom_components.myair3.MyAir3ApiClient", return_value=mock_client):
        mock_config_entry.add_to_hass(hass)
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()
    return mock_client


async def test_system_temperature_sensor_value(hass, setup_sensor):
    """Test that the system temperature sensor reports the correct value."""
    state = hass.states.get("sensor.test_aircon_temperature")
    assert state is not None
    assert float(state.state) == 24.0


async def test_sensor_unique_ids(hass, mock_config_entry, setup_sensor):
    """Test that sensors have correct unique IDs."""
    entry_id = mock_config_entry.entry_id

    from homeassistant.helpers import entity_registry as er_module
    registry = er_module.async_get(hass)

    temp_entry = registry.async_get("sensor.test_aircon_temperature")
    assert temp_entry is not None
    assert temp_entry.unique_id == f"{entry_id}_temperature"


async def test_sensor_device_info(hass, mock_config_entry, setup_sensor):
    """Test that sensors have correct device info."""
    from homeassistant.helpers import device_registry as dr_module
    device_registry = dr_module.async_get(hass)

    entry_id = mock_config_entry.entry_id
    device = device_registry.async_get_device(identifiers={(DOMAIN, entry_id)})
    assert device is not None
    assert device.name == "Test Aircon"
    assert device.manufacturer == "Advantage Air"
    assert device.model == "MyAir3"
