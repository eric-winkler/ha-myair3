"""Base entity for MyAir3."""
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
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_zone_{zone_id}")},
            name=coordinator.data["zones"][zone_id]["name"],
            manufacturer="Advantage Air",
            model="MyAir3 Zone",
            via_device=(DOMAIN, entry.entry_id),
        )
