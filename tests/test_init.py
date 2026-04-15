"""Tests for MyAir3 integration setup and teardown."""
from unittest.mock import AsyncMock, patch


from custom_components.myair3.api import MyAir3ApiError

from .conftest import MOCK_SYSTEM_DATA


async def test_setup_entry(hass, mock_config_entry, mock_client, enable_custom_integrations):
    """Test that async_setup_entry sets up coordinator and platforms."""
    with patch("custom_components.myair3.async_get_clientsession"), \
         patch("custom_components.myair3.MyAir3ApiClient", return_value=mock_client):
        mock_config_entry.add_to_hass(hass)
        result = await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert result is True
    assert mock_config_entry.runtime_data is not None
    assert mock_config_entry.runtime_data.data == MOCK_SYSTEM_DATA


async def test_unload_entry(hass, mock_config_entry, mock_client, enable_custom_integrations):
    """Test that async_unload_entry unloads correctly."""
    with patch("custom_components.myair3.async_get_clientsession"), \
         patch("custom_components.myair3.MyAir3ApiClient", return_value=mock_client):
        mock_config_entry.add_to_hass(hass)
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    result = await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert result is True


async def test_setup_failure_returns_false(hass, mock_config_entry, mock_client, enable_custom_integrations):
    """Test that a coordinator refresh failure causes setup to fail."""
    mock_client.get_system_data = AsyncMock(side_effect=MyAir3ApiError("fail"))
    with patch("custom_components.myair3.async_get_clientsession"), \
         patch("custom_components.myair3.MyAir3ApiClient", return_value=mock_client):
        mock_config_entry.add_to_hass(hass)
        result = await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert result is False
