"""Tests for MyAir3 cover platform."""
from unittest.mock import patch

import pytest
from homeassistant.components.cover import ATTR_POSITION

from custom_components.myair3.const import DOMAIN


@pytest.fixture
async def setup_cover(hass, mock_config_entry, mock_client, enable_custom_integrations):
    """Set up the cover platform for testing."""
    with patch("custom_components.myair3.async_get_clientsession"), \
         patch("custom_components.myair3.MyAir3ApiClient", return_value=mock_client):
        mock_config_entry.add_to_hass(hass)
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()
    return mock_client


async def test_cover_entities_created(hass, setup_cover):
    """Test that cover entities are created for each zone."""
    assert hass.states.get("cover.living_room_damper") is not None
    assert hass.states.get("cover.bedroom_damper") is not None


async def test_zone1_position(hass, setup_cover):
    """Test that zone 1 cover reports correct position."""
    state = hass.states.get("cover.living_room_damper")
    assert state is not None
    assert state.attributes["current_position"] == 80


async def test_zone2_position(hass, setup_cover):
    """Test that zone 2 cover reports correct position."""
    state = hass.states.get("cover.bedroom_damper")
    assert state is not None
    assert state.attributes["current_position"] == 0


async def test_is_closed_when_damper_zero(hass, setup_cover):
    """Test that is_closed returns True when damper is 0%."""
    state = hass.states.get("cover.bedroom_damper")
    assert state is not None
    assert state.state == "closed"


async def test_is_open_when_damper_nonzero(hass, setup_cover):
    """Test that is_closed returns False when damper is non-zero."""
    state = hass.states.get("cover.living_room_damper")
    assert state is not None
    assert state.state == "open"


async def test_open_cover(hass, setup_cover):
    """Test that open_cover sets damper to 100%."""
    client = setup_cover
    await hass.services.async_call(
        "cover",
        "open_cover",
        {"entity_id": "cover.living_room_damper"},
        blocking=True,
    )
    client.set_zone_data.assert_called_with(
        zone_number=1,
        enabled=True,
        damper_percent=100,
        name="Living Room",
    )


async def test_close_cover(hass, setup_cover):
    """Test that close_cover sets damper to 0% and enabled=False."""
    client = setup_cover
    await hass.services.async_call(
        "cover",
        "close_cover",
        {"entity_id": "cover.living_room_damper"},
        blocking=True,
    )
    client.set_zone_data.assert_called_with(
        zone_number=1,
        enabled=False,
        damper_percent=0,
        name="Living Room",
    )


async def test_set_position_exact_multiple_of_10(hass, setup_cover):
    """Test set_cover_position with a value already a multiple of 10."""
    client = setup_cover
    await hass.services.async_call(
        "cover",
        "set_cover_position",
        {"entity_id": "cover.living_room_damper", ATTR_POSITION: 80},
        blocking=True,
    )
    client.set_zone_data.assert_called_with(
        zone_number=1,
        enabled=True,
        damper_percent=80,
        name="Living Room",
    )


async def test_set_position_rounds_up(hass, setup_cover):
    """Test set_cover_position rounds 96 to 100."""
    client = setup_cover
    await hass.services.async_call(
        "cover",
        "set_cover_position",
        {"entity_id": "cover.living_room_damper", ATTR_POSITION: 96},
        blocking=True,
    )
    client.set_zone_data.assert_called_with(
        zone_number=1,
        enabled=True,
        damper_percent=100,
        name="Living Room",
    )


async def test_set_position_rounds_down(hass, setup_cover):
    """Test set_cover_position rounds 84 to 80."""
    client = setup_cover
    await hass.services.async_call(
        "cover",
        "set_cover_position",
        {"entity_id": "cover.living_room_damper", ATTR_POSITION: 84},
        blocking=True,
    )
    client.set_zone_data.assert_called_with(
        zone_number=1,
        enabled=True,
        damper_percent=80,
        name="Living Room",
    )


async def test_set_position_rounds_half_up(hass, setup_cover):
    """Test set_cover_position rounds 85 to 90."""
    client = setup_cover
    await hass.services.async_call(
        "cover",
        "set_cover_position",
        {"entity_id": "cover.living_room_damper", ATTR_POSITION: 85},
        blocking=True,
    )
    client.set_zone_data.assert_called_with(
        zone_number=1,
        enabled=True,
        damper_percent=90,
        name="Living Room",
    )


async def test_set_position_zero_disables(hass, setup_cover):
    """Test set_cover_position with 0 sets enabled=False."""
    client = setup_cover
    await hass.services.async_call(
        "cover",
        "set_cover_position",
        {"entity_id": "cover.living_room_damper", ATTR_POSITION: 0},
        blocking=True,
    )
    client.set_zone_data.assert_called_with(
        zone_number=1,
        enabled=False,
        damper_percent=0,
        name="Living Room",
    )


async def test_cover_unique_ids(hass, mock_config_entry, setup_cover):
    """Test that cover entities have correct unique IDs."""
    entry_id = mock_config_entry.entry_id

    from homeassistant.helpers import entity_registry as er_module
    registry = er_module.async_get(hass)

    zone1_entry = registry.async_get("cover.living_room_damper")
    assert zone1_entry is not None
    assert zone1_entry.unique_id == f"{entry_id}_zone_1_damper"

    zone2_entry = registry.async_get("cover.bedroom_damper")
    assert zone2_entry is not None
    assert zone2_entry.unique_id == f"{entry_id}_zone_2_damper"


async def test_cover_device_info(hass, mock_config_entry, setup_cover):
    """Test that cover entities are associated with the correct zone device."""
    from homeassistant.helpers import device_registry as dr_module
    device_registry = dr_module.async_get(hass)

    entry_id = mock_config_entry.entry_id
    zone_device = device_registry.async_get_device(
        identifiers={(DOMAIN, f"{entry_id}_zone_1")}
    )
    assert zone_device is not None
    assert zone_device.name == "Living Room"
    assert zone_device.manufacturer == "Advantage Air"
    assert zone_device.model == "MyAir3 Zone"
