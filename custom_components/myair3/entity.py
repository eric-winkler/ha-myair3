"""Base entity for MyAir3."""
import inspect

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MyAir3Coordinator


class MyAir3Entity(CoordinatorEntity[MyAir3Coordinator]):
    """Base entity for MyAir3 devices."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: MyAir3Coordinator) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=coordinator.data["system"]["name"],
            manufacturer="Advantage Air",
            model="MyAir3",
        )


class MyAir3ZoneEntity(MyAir3Entity):
    """Base entity for MyAir3 zone devices."""

    def __init__(self, coordinator: MyAir3Coordinator, zone_id: int) -> None:
        super().__init__(coordinator)
        self.zone_id = zone_id
        entry = coordinator.config_entry
        device_registry = dr.async_get(coordinator.hass)
        parent_identifier = (DOMAIN, entry.entry_id)
        parent_device = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={parent_identifier},
            name=coordinator.data["system"]["name"],
            manufacturer="Advantage Air",
            model="MyAir3",
        )

        device_info_kwargs = {
            "identifiers": {(DOMAIN, f"{entry.entry_id}_zone_{zone_id}")},
            "name": coordinator.data["zones"][zone_id]["name"],
            "manufacturer": "Advantage Air",
            "model": "MyAir3 Zone",
        }
        if "via_device_id" in inspect.signature(
            device_registry.async_get_or_create
        ).parameters:
            device_info_kwargs["via_device_id"] = parent_device.id
        else:
            device_info_kwargs["via_device"] = parent_identifier

        self._attr_device_info = DeviceInfo(
            **device_info_kwargs,
        )
