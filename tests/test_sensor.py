"""Tests for MyAir3 sensor platform."""
from unittest.mock import patch

import pytest

from custom_components.myair3.const import DOMAIN

from .conftest import MOCK_IP, MOCK_SYSTEM_DATA


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


async def test_zone1_damper_sensor(hass, setup_sensor):
    """Test zone 1 damper sensor."""
    state = hass.states.get("sensor.living_room_damper")
    assert state is not None
    assert int(state.state) == 80


async def test_zone2_damper_sensor(hass, setup_sensor):
    """Test zone 2 damper sensor."""
    state = hass.states.get("sensor.bedroom_damper")
    assert state is not None
    assert int(state.state) == 0


async def test_sensor_unique_ids(hass, mock_config_entry, setup_sensor):
    """Test that sensors have correct unique IDs."""
    entry_id = mock_config_entry.entry_id

    from homeassistant.helpers import entity_registry as er_module
    registry = er_module.async_get(hass)

    temp_entry = registry.async_get("sensor.test_aircon_temperature")
    assert temp_entry is not None
    assert temp_entry.unique_id == f"{entry_id}_temperature"

    zone1_entry = registry.async_get("sensor.living_room_damper")
    assert zone1_entry is not None
    assert zone1_entry.unique_id == f"{entry_id}_zone_1_damper"

    zone2_entry = registry.async_get("sensor.bedroom_damper")
    assert zone2_entry is not None
    assert zone2_entry.unique_id == f"{entry_id}_zone_2_damper"


async def test_sensor_device_info(hass, mock_config_entry, setup_sensor):
    """Test that sensors have correct device info."""
    from homeassistant.helpers import device_registry as dr_module
    device_registry = dr_module.async_get(hass)

    # System device
    entry_id = mock_config_entry.entry_id
    device = device_registry.async_get_device(identifiers={(DOMAIN, entry_id)})
    assert device is not None
    assert device.name == "Test Aircon"
    assert device.manufacturer == "Advantage Air"
    assert device.model == "MyAir3"

    # Zone device
    zone_device = device_registry.async_get_device(
        identifiers={(DOMAIN, f"{entry_id}_zone_1")}
    )
    assert zone_device is not None
    assert zone_device.name == "Living Room"
    assert zone_device.manufacturer == "Advantage Air"
    assert zone_device.model == "MyAir3 Zone"
