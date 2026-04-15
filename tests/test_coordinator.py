"""Tests for MyAir3 DataUpdateCoordinator."""
from datetime import timedelta
from unittest.mock import AsyncMock

from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.myair3.api import MyAir3ApiError
from custom_components.myair3.const import UPDATE_INTERVAL_SECONDS
from custom_components.myair3.coordinator import MyAir3Coordinator

from .conftest import MOCK_SYSTEM_DATA


async def test_successful_update(hass, mock_config_entry, mock_client):
    """Test successful data update populates coordinator data."""
    coordinator = MyAir3Coordinator(hass, mock_config_entry, mock_client)
    await coordinator.async_refresh()
    assert coordinator.data == MOCK_SYSTEM_DATA
    mock_client.get_system_data.assert_called_once()


async def test_api_error_raises_update_failed(hass, mock_config_entry, mock_client):
    """Test that MyAir3ApiError is converted to UpdateFailed."""
    mock_client.get_system_data = AsyncMock(side_effect=MyAir3ApiError("connection error"))
    coordinator = MyAir3Coordinator(hass, mock_config_entry, mock_client)
    await coordinator.async_refresh()
    assert coordinator.last_update_success is False
    assert isinstance(coordinator.last_exception, UpdateFailed)
    assert "Error communicating with MyAir3 API" in str(coordinator.last_exception)


async def test_update_interval(hass, mock_config_entry, mock_client):
    """Test that the update interval matches the constant."""
    coordinator = MyAir3Coordinator(hass, mock_config_entry, mock_client)
    assert coordinator.update_interval == timedelta(seconds=UPDATE_INTERVAL_SECONDS)
