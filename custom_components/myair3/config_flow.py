"""Config flow for MyAir3."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MyAir3ApiClient, MyAir3ApiError
from .const import DOMAIN

MYAIR3_SCHEMA = vol.Schema({vol.Required(CONF_IP_ADDRESS): str})


class MyAir3ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for MyAir3."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a user-initiated config flow."""
        errors: dict[str, str] = {}
        if user_input is not None:
            ip = user_input[CONF_IP_ADDRESS]
            await self.async_set_unique_id(ip)
            self._abort_if_unique_id_configured()
            session = async_get_clientsession(self.hass)
            client = MyAir3ApiClient(ip, session)
            try:
                await client.validate_connection()
            except MyAir3ApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title=ip, data=user_input)
        return self.async_show_form(
            step_id="user", data_schema=MYAIR3_SCHEMA, errors=errors
        )
