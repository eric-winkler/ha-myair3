"""Tests for MyAir3 API client."""
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from custom_components.myair3.api import MyAir3ApiClient, MyAir3ApiError

MOCK_IP = "192.168.1.100"

SYSTEM_XML = """<?xml version="1.0" encoding="UTF-8" ?>
<iZS10.3>
  <request>getSystemData</request>
  <mac>001ec0a3cf20</mac>
  <authenticated>1</authenticated>
  <system>
    <type>103</type>
    <name>Test Aircon</name>
    <MyAppRev>2.0</MyAppRev>
    <ip>192.168.1.100</ip>
    <unitcontrol>
      <airconOnOff>1</airconOnOff>
      <fanSpeed>2</fanSpeed>
      <mode>1</mode>
      <centralActualTemp>24.0</centralActualTemp>
      <centralDesiredTemp>22.0</centralDesiredTemp>
      <numberOfZones>2</numberOfZones>
      <maxUserTemp>32.0</maxUserTemp>
      <minUserTemp>16.0</minUserTemp>
      <airConErrorCode>0</airConErrorCode>
    </unitcontrol>
  </system>
</iZS10.3>"""

ZONE1_XML = """<aircon>
  <zone1>
    <name>Living Room</name>
    <setting>1</setting>
    <userPercentSetting>80</userPercentSetting>
  </zone1>
</aircon>"""

ZONE2_XML = """<aircon>
  <zone2>
    <name>Bedroom</name>
    <setting>0</setting>
    <userPercentSetting>0</userPercentSetting>
  </zone2>
</aircon>"""

AUTH_FAIL_XML = "<response><authenticated>0</authenticated></response>"
AUTH_SUCCESS_XML = "<authenticated>1</authenticated>"
SET_OK_XML = "<response><status>ok</status></response>"


def _mock_response(body: str):
    resp = AsyncMock()
    resp.status = 200
    resp.text = AsyncMock(return_value=body)
    resp.raise_for_status = MagicMock()
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=False)
    return resp


def _mock_session(*bodies):
    session = MagicMock()
    session.get = MagicMock(side_effect=[_mock_response(b) for b in bodies])
    return session


async def test_login_success():
    client = MyAir3ApiClient(MOCK_IP, _mock_session(AUTH_SUCCESS_XML))
    await client._login()


async def test_login_failure():
    client = MyAir3ApiClient(MOCK_IP, _mock_session(AUTH_FAIL_XML))
    with pytest.raises(MyAir3ApiError, match="Login failed"):
        await client._login()


async def test_get_system_data_parses_correctly():
    client = MyAir3ApiClient(MOCK_IP, _mock_session(SYSTEM_XML, ZONE1_XML, ZONE2_XML))
    data = await client.get_system_data()

    assert data["system"]["name"] == "Test Aircon"
    assert data["system"]["type"] == 103
    assert data["system"]["my_app_rev"] == "2.0"
    assert data["system"]["ip"] == MOCK_IP

    uc = data["unitcontrol"]
    assert uc["power_on"] is True
    assert uc["fan_speed"] == 2
    assert uc["mode"] == 1
    assert uc["central_actual_temp"] == 24.0
    assert uc["central_desired_temp"] == 22.0
    assert uc["min_temp"] == 16.0
    assert uc["max_temp"] == 32.0
    assert uc["number_of_zones"] == 2
    assert uc["error_code"] == "0"


async def test_get_zone_data_called_for_each_zone():
    client = MyAir3ApiClient(MOCK_IP, _mock_session(SYSTEM_XML, ZONE1_XML, ZONE2_XML))
    data = await client.get_system_data()

    assert 1 in data["zones"]
    assert 2 in data["zones"]
    assert data["zones"][1]["name"] == "Living Room"
    assert data["zones"][1]["enabled"] is True
    assert data["zones"][1]["damper_percent"] == 80
    assert data["zones"][2]["name"] == "Bedroom"
    assert data["zones"][2]["enabled"] is False
    assert data["zones"][2]["damper_percent"] == 0


async def test_set_system_data_sends_correct_params():
    session = _mock_session(SET_OK_XML)
    client = MyAir3ApiClient(MOCK_IP, session)
    await client.set_system_data(airconOnOff=1, fanSpeed=2)
    session.get.assert_called_once()
    _, call_kwargs = session.get.call_args
    params = call_kwargs.get("params", {})
    assert params.get("airconOnOff") == 1
    assert params.get("fanSpeed") == 2


async def test_set_zone_data_sends_correct_params():
    session = _mock_session(SET_OK_XML)
    client = MyAir3ApiClient(MOCK_IP, session)
    await client.set_zone_data(zone_number=1, enabled=True, damper_percent=80, name="Living Room")
    session.get.assert_called_once()
    _, call_kwargs = session.get.call_args
    params = call_kwargs.get("params", {})
    assert params.get("zone") == 1
    assert params.get("zoneSetting") == 1
    assert params.get("userPercentSetting") == 80
    assert params.get("name") == "Living Room"


async def test_zone_setting_zero_overrides_user_percent():
    """When zoneSetting=0, damper_percent must be 0 regardless of userPercentSetting."""
    zone_with_setting_off_xml = """<aircon>
  <zone1>
    <name>Living Room</name>
    <setting>0</setting>
    <userPercentSetting>30</userPercentSetting>
  </zone1>
</aircon>"""
    zone2_xml = """<aircon>
  <zone2>
    <name>Bedroom</name>
    <setting>0</setting>
    <userPercentSetting>0</userPercentSetting>
  </zone2>
</aircon>"""
    client = MyAir3ApiClient(
        MOCK_IP, _mock_session(SYSTEM_XML, zone_with_setting_off_xml, zone2_xml)
    )
    data = await client.get_system_data()
    assert data["zones"][1]["enabled"] is False
    assert data["zones"][1]["damper_percent"] == 0
    assert data["zones"][2]["enabled"] is False
    assert data["zones"][2]["damper_percent"] == 0


async def test_auto_login_on_auth_failure():
    """When first request returns auth failure, retries after login."""
    client = MyAir3ApiClient(
        MOCK_IP,
        _mock_session(AUTH_FAIL_XML, AUTH_SUCCESS_XML, SYSTEM_XML, ZONE1_XML, ZONE2_XML),
    )
    data = await client.get_system_data()
    assert data["system"]["name"] == "Test Aircon"


async def test_timeout_raises_api_error():
    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(side_effect=aiohttp.ServerTimeoutError())
    ctx.__aexit__ = AsyncMock(return_value=False)
    session = MagicMock()
    session.get = MagicMock(return_value=ctx)

    client = MyAir3ApiClient(MOCK_IP, session)
    with pytest.raises(MyAir3ApiError):
        await client._request("/getSystemData")


async def test_validate_connection_returns_true():
    client = MyAir3ApiClient(MOCK_IP, _mock_session(SYSTEM_XML))
    assert await client.validate_connection() is True
