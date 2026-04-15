"""Config flow for the MyAir3 integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MyAir3Api, MyAir3ApiError
from .const import CONF_HOST, CONF_PORT, DEFAULT_PORT, DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
    }
)


class MyAir3ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MyAir3."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step where the user enters the controller address."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            api = MyAir3Api(host, port, async_get_clientsession(self.hass))
            try:
                data = await api.async_get_data()
            except MyAir3ApiError:
                errors["base"] = "cannot_connect"
            else:
                # Use the host as a unique identifier for this controller.
                await self.async_set_unique_id(f"{host}:{port}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=data["system"]["name"] or host,
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
