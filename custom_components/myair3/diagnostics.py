"""Diagnostics for MyAir3."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .coordinator import MyAir3ConfigEntry

TO_REDACT = {"ip", "ip_address"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: MyAir3ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "data": async_redact_data(coordinator.data, TO_REDACT),
    }
