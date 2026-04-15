"""API client for MyAir3."""
from __future__ import annotations

import xml.etree.ElementTree as ET

import aiohttp

from .const import DEFAULT_TIMEOUT


class MyAir3ApiError(Exception):
    """Exception for MyAir3 API errors."""


class MyAir3ApiClient:
    """Client for the MyAir3 HTTP API."""

    def __init__(
        self,
        ip: str,
        session: aiohttp.ClientSession,
        password: str = "",
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self._base_url = f"http://{ip}"
        self._session = session
        self._password = password
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    async def _request(self, path: str, **params) -> str:
        url = f"{self._base_url}{path}"
        try:
            async with self._session.get(
                url, params=params, timeout=self._timeout
            ) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as err:
            raise MyAir3ApiError(f"Request failed: {err}") from err
        except TimeoutError as err:
            raise MyAir3ApiError(f"Request timed out: {err}") from err

    async def _login(self) -> None:
        text = await self._request("/login", password=self._password)
        if "<authenticated>1</authenticated>" not in text:
            raise MyAir3ApiError("Login failed: invalid credentials")

    async def _authenticated_request(self, path: str, **params) -> str:
        text = await self._request(path, **params)
        if "<authenticated>0</authenticated>" in text:
            await self._login()
            text = await self._request(path, **params)
        return text

    async def validate_connection(self) -> bool:
        """Validate the connection to the device."""
        await self._authenticated_request("/getSystemData")
        return True

    async def get_system_data(self) -> dict:
        """Get all system and zone data."""
        text = await self._authenticated_request("/getSystemData")
        root = ET.fromstring(text)

        system_data = {
            "name": root.findtext("name", ""),
            "type": int(root.findtext("type", "0") or 0),
            "my_app_rev": root.findtext("MyAppRev", ""),
            "ip": root.findtext("ip", ""),
        }

        uc = root.find("unitcontrol")
        if uc is None:
            raise MyAir3ApiError("Missing unitcontrol in system data")

        number_of_zones = int(uc.findtext("numberOfZones", "0") or 0)
        unitcontrol_data = {
            "power_on": uc.findtext("airconOnOff", "0") == "1",
            "fan_speed": int(uc.findtext("fanSpeed", "1") or 1),
            "mode": int(uc.findtext("mode", "1") or 1),
            "central_actual_temp": float(uc.findtext("centralActualTemp", "0") or 0),
            "central_desired_temp": float(uc.findtext("centralDesiredTemp", "0") or 0),
            "min_temp": float(uc.findtext("minUserTemp", "16") or 16),
            "max_temp": float(uc.findtext("maxUserTemp", "32") or 32),
            "number_of_zones": number_of_zones,
            "error_code": uc.findtext("airConErrorCode", "0") or "0",
        }

        zones: dict[int, dict] = {}
        for zone_num in range(1, number_of_zones + 1):
            zone_text = await self._authenticated_request(
                "/getZoneData", zone=zone_num
            )
            zone_root = ET.fromstring(zone_text)
            zone_el = zone_root.find(f"zone{zone_num}")
            if zone_el is not None:
                zones[zone_num] = {
                    "name": zone_el.findtext("name", f"Zone {zone_num}"),
                    "enabled": zone_el.findtext("setting", "0") == "1",
                    "damper_percent": int(
                        zone_el.findtext("userPercentSetting", "0") or 0
                    ),
                }
            else:
                zones[zone_num] = {
                    "name": f"Zone {zone_num}",
                    "enabled": False,
                    "damper_percent": 0,
                }

        return {
            "system": system_data,
            "unitcontrol": unitcontrol_data,
            "zones": zones,
        }

    async def set_system_data(self, **kwargs) -> None:
        """Set system parameters."""
        await self._authenticated_request("/setSystemData", **kwargs)

    async def set_zone_data(
        self,
        zone_number: int,
        enabled: bool,
        damper_percent: int,
        name: str,
    ) -> None:
        """Set zone parameters."""
        await self._authenticated_request(
            "/setZoneData",
            zone=zone_number,
            zoneSetting=1 if enabled else 0,
            userPercentSetting=damper_percent,
            name=name,
        )
