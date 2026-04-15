"""Tests for MyAir3 config flow."""
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.myair3.api import MyAir3ApiError
from custom_components.myair3.const import DOMAIN

MOCK_IP = "192.168.1.100"


async def test_form_shown_on_initial_step(hass, enable_custom_integrations):
    """Test that the form is shown on the initial step."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert not result["errors"]


async def test_successful_config_creates_entry(hass, mock_client, enable_custom_integrations):
    """Test that a successful connection creates a config entry."""
    with patch("custom_components.myair3.config_flow.async_get_clientsession"), \
         patch("custom_components.myair3.config_flow.MyAir3ApiClient.validate_connection", return_value=True), \
         patch("custom_components.myair3.async_get_clientsession"), \
         patch("custom_components.myair3.MyAir3ApiClient", return_value=mock_client):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data={CONF_IP_ADDRESS: MOCK_IP},
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == MOCK_IP
    assert result["data"] == {CONF_IP_ADDRESS: MOCK_IP}


async def test_cannot_connect_error(hass, enable_custom_integrations):
    """Test that a connection failure shows an error."""
    with patch("custom_components.myair3.config_flow.async_get_clientsession"), \
         patch(
             "custom_components.myair3.config_flow.MyAir3ApiClient.validate_connection",
             side_effect=MyAir3ApiError("cannot connect"),
         ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data={CONF_IP_ADDRESS: MOCK_IP},
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_duplicate_entry_aborts(hass, enable_custom_integrations):
    """Test that adding an already-configured device aborts."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_IP_ADDRESS: MOCK_IP},
        unique_id=MOCK_IP,
    )
    entry.add_to_hass(hass)

    with patch("custom_components.myair3.config_flow.async_get_clientsession"), \
         patch(
             "custom_components.myair3.config_flow.MyAir3ApiClient.validate_connection",
             return_value=True,
         ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data={CONF_IP_ADDRESS: MOCK_IP},
        )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"
