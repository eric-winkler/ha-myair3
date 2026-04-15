"""Tests for MyAir3 climate platform."""
from unittest.mock import patch

import pytest
from homeassistant.components.climate import HVACMode
from homeassistant.const import ATTR_TEMPERATURE




@pytest.fixture
async def setup_climate(hass, mock_config_entry, mock_client, enable_custom_integrations):
    """Set up the climate platform for testing."""
    with patch("custom_components.myair3.async_get_clientsession"), \
         patch("custom_components.myair3.MyAir3ApiClient", return_value=mock_client):
        mock_config_entry.add_to_hass(hass)
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()
    return mock_client


async def test_climate_state_reporting(hass, setup_climate):
    """Test that climate entity reports correct state."""
    state = hass.states.get("climate.test_aircon")
    assert state is not None
    assert state.state == HVACMode.COOL
    assert state.attributes["current_temperature"] == 24.0
    assert state.attributes["temperature"] == 22.0
    assert state.attributes["fan_mode"] == "medium"
    assert state.attributes["min_temp"] == 16.0
    assert state.attributes["max_temp"] == 32.0


async def test_climate_turn_on(hass, setup_climate):
    """Test turning the climate on."""
    client = setup_climate
    await hass.services.async_call(
        "climate",
        "turn_on",
        {"entity_id": "climate.test_aircon"},
        blocking=True,
    )
    client.set_system_data.assert_called_with(airconOnOff=1)


async def test_climate_turn_off(hass, setup_climate):
    """Test turning the climate off."""
    client = setup_climate
    await hass.services.async_call(
        "climate",
        "turn_off",
        {"entity_id": "climate.test_aircon"},
        blocking=True,
    )
    client.set_system_data.assert_called_with(airconOnOff=0)


async def test_set_hvac_mode_cool(hass, setup_climate):
    """Test setting HVAC mode to cool."""
    client = setup_climate
    await hass.services.async_call(
        "climate",
        "set_hvac_mode",
        {"entity_id": "climate.test_aircon", "hvac_mode": HVACMode.COOL},
        blocking=True,
    )
    client.set_system_data.assert_called_with(airconOnOff=1, mode=1)


async def test_set_hvac_mode_heat(hass, setup_climate):
    """Test setting HVAC mode to heat."""
    client = setup_climate
    await hass.services.async_call(
        "climate",
        "set_hvac_mode",
        {"entity_id": "climate.test_aircon", "hvac_mode": HVACMode.HEAT},
        blocking=True,
    )
    client.set_system_data.assert_called_with(airconOnOff=1, mode=2)


async def test_set_hvac_mode_fan_only(hass, setup_climate):
    """Test setting HVAC mode to fan only."""
    client = setup_climate
    await hass.services.async_call(
        "climate",
        "set_hvac_mode",
        {"entity_id": "climate.test_aircon", "hvac_mode": HVACMode.FAN_ONLY},
        blocking=True,
    )
    client.set_system_data.assert_called_with(airconOnOff=1, mode=3)


async def test_set_hvac_mode_off(hass, setup_climate):
    """Test setting HVAC mode to off."""
    client = setup_climate
    await hass.services.async_call(
        "climate",
        "set_hvac_mode",
        {"entity_id": "climate.test_aircon", "hvac_mode": HVACMode.OFF},
        blocking=True,
    )
    client.set_system_data.assert_called_with(airconOnOff=0)


async def test_set_fan_mode_low(hass, setup_climate):
    """Test setting fan mode to low."""
    client = setup_climate
    await hass.services.async_call(
        "climate",
        "set_fan_mode",
        {"entity_id": "climate.test_aircon", "fan_mode": "low"},
        blocking=True,
    )
    client.set_system_data.assert_called_with(fanSpeed=1)


async def test_set_fan_mode_medium(hass, setup_climate):
    """Test setting fan mode to medium."""
    client = setup_climate
    await hass.services.async_call(
        "climate",
        "set_fan_mode",
        {"entity_id": "climate.test_aircon", "fan_mode": "medium"},
        blocking=True,
    )
    client.set_system_data.assert_called_with(fanSpeed=2)


async def test_set_fan_mode_high(hass, setup_climate):
    """Test setting fan mode to high."""
    client = setup_climate
    await hass.services.async_call(
        "climate",
        "set_fan_mode",
        {"entity_id": "climate.test_aircon", "fan_mode": "high"},
        blocking=True,
    )
    client.set_system_data.assert_called_with(fanSpeed=3)


async def test_set_temperature(hass, setup_climate):
    """Test setting the target temperature."""
    client = setup_climate
    await hass.services.async_call(
        "climate",
        "set_temperature",
        {"entity_id": "climate.test_aircon", ATTR_TEMPERATURE: 25.0},
        blocking=True,
    )
    client.set_system_data.assert_called_with(centralDesiredTemp=25.0)
