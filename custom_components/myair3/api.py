"""MyAir3 HTTP/XML API client."""

from __future__ import annotations

import asyncio
import logging
from urllib.parse import quote
from xml.etree import ElementTree

from aiohttp import ClientError, ClientSession

_LOGGER = logging.getLogger(__name__)


class MyAir3ApiError(Exception):
    """Error raised when the MyAir3 API returns an error or is unreachable."""


class MyAir3Api:
    """Async client for the MyAir3 aircon controller HTTP API.

    The MyAir3 controller exposes a simple HTTP GET API with XML responses.
    Authentication uses a session cookie obtained via the login endpoint.
    """

    def __init__(self, host: str, port: int, session: ClientSession) -> None:
        """Initialise the API client.

        Args:
            host: IP address or hostname of the controller.
            port: TCP port (default 80).
            session: Shared aiohttp ClientSession (must persist cookies).
        """
        self._host = host
        self._port = port
        self._session = session
        self._base_url = f"http://{host}:{port}"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _get(self, endpoint: str) -> ElementTree.Element:
        """Make a GET request and return the parsed XML root element.

        Transparently handles reauthentication: if the response indicates the
        session is not authenticated the login endpoint is called first and
        the original request is retried once.
        """
        url = f"{self._base_url}/{endpoint}"
        root = await self._raw_get(url)

        auth_elem = root.find("authenticated")
        if auth_elem is None or auth_elem.text != "1":
            _LOGGER.debug("Not authenticated, logging in")
            await self._login()
            root = await self._raw_get(url)

        return root

    async def _raw_get(self, url: str) -> ElementTree.Element:
        """Perform a single HTTP GET and return the parsed XML."""
        try:
            async with self._session.get(url, timeout=5) as resp:
                text = await resp.text()
        except ClientError as err:
            raise MyAir3ApiError(f"HTTP request failed: {err}") from err
        except asyncio.TimeoutError as err:
            raise MyAir3ApiError("HTTP request timed out") from err

        try:
            return ElementTree.fromstring(text)
        except ElementTree.ParseError as err:
            raise MyAir3ApiError(f"Failed to parse XML response: {err}") from err

    async def _login(self) -> None:
        """Authenticate with the controller using the default password."""
        url = f"{self._base_url}/login?password=password"
        try:
            async with self._session.get(url, timeout=5) as resp:
                await resp.text()
        except (ClientError, asyncio.TimeoutError) as err:
            raise MyAir3ApiError(f"Login request failed: {err}") from err

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    async def async_get_data(self) -> dict:
        """Fetch all system and zone data and return as a normalised dict.

        Returns a dict with two keys:
          "system"  – unit-level information and settings
          "zones"   – dict keyed by zone number (int) with per-zone data
        """
        root = await self._get("getSystemData")

        system_elem = root.find("system")
        if system_elem is None:
            raise MyAir3ApiError("Unexpected response: missing <system> element")

        unit_control = system_elem.find("unitcontrol")
        if unit_control is None:
            raise MyAir3ApiError(
                "Unexpected response: missing <unitcontrol> element"
            )

        def _int(elem_name: str, parent: ElementTree.Element = unit_control) -> int:
            el = parent.find(elem_name)
            if el is None or el.text is None:
                raise MyAir3ApiError(
                    f"Unexpected response: missing <{elem_name}> element"
                )
            return int(el.text)

        def _float(elem_name: str, parent: ElementTree.Element = unit_control) -> float:
            el = parent.find(elem_name)
            if el is None or el.text is None:
                raise MyAir3ApiError(
                    f"Unexpected response: missing <{elem_name}> element"
                )
            return float(el.text)

        def _str(elem_name: str, parent: ElementTree.Element = unit_control) -> str:
            el = parent.find(elem_name)
            return el.text if el is not None and el.text is not None else ""

        num_zones = _int("numberOfZones")

        system_data: dict = {
            "name": _str("name", system_elem),
            "type": _int("type", system_elem),
            "app_revision": _str("MyAppRev", system_elem),
            "power": _int("airconOnOff") == 1,
            "fan_speed": _int("fanSpeed"),
            "mode": _int("mode"),
            "central_actual_temp": _float("centralActualTemp"),
            "central_desired_temp": _float("centralDesiredTemp"),
            "error_code": _str("airConErrorCode"),
            "num_zones": num_zones,
            "max_temp": _float("maxUserTemp"),
            "min_temp": _float("minUserTemp"),
        }

        # Fetch all zone data concurrently
        zone_tasks = [
            asyncio.create_task(self._get(f"getZoneData?zone={z}"))
            for z in range(1, num_zones + 1)
        ]
        zone_roots = await asyncio.gather(*zone_tasks, return_exceptions=True)

        zones: dict[int, dict] = {}
        for idx, result in enumerate(zone_roots):
            zone_num = idx + 1
            if isinstance(result, Exception):
                _LOGGER.warning("Failed to fetch zone %d data: %s", zone_num, result)
                continue
            zone_elem = result.find(f"zone{zone_num}")
            if zone_elem is None:
                _LOGGER.warning(
                    "Zone %d data missing expected element <zone%d>",
                    zone_num,
                    zone_num,
                )
                continue

            def _zone_int(name: str) -> int:
                el = zone_elem.find(name)
                return int(el.text) if el is not None and el.text is not None else 0

            def _zone_float(name: str) -> float:
                el = zone_elem.find(name)
                return float(el.text) if el is not None and el.text is not None else 0.0

            def _zone_str(name: str) -> str:
                el = zone_elem.find(name)
                return el.text if el is not None and el.text is not None else ""

            zones[zone_num] = {
                "name": _zone_str("name"),
                "enabled": _zone_int("setting") == 1,
                "user_percent": _zone_int("userPercentSetting"),
                "user_percent_available": _zone_int("userPercentAvail") == 1,
                "actual_temp": _zone_float("actualTemp"),
                "desired_temp": _zone_float("desiredTemp"),
                "has_climate_control": _zone_int("hasClimateControl") == 1,
                "has_low_battery": _zone_int("hasLowBatt") == 1,
                "has_motor_error": _zone_int("hasMotorError") == 1,
            }

        return {"system": system_data, "zones": zones}

    async def async_set_system_data(
        self,
        power: bool,
        fan_speed: int,
        mode: int,
        central_desired_temp: float,
    ) -> None:
        """Update the AC unit settings."""
        await self._get(
            f"setSystemData?airconOnOff={1 if power else 0}"
            f"&fanSpeed={fan_speed}"
            f"&mode={mode}"
            f"&centralDesiredTemp={central_desired_temp}"
        )

    async def async_set_zone_data(
        self,
        zone_num: int,
        enabled: bool,
        name: str,
        user_percent: int,
    ) -> None:
        """Update a zone's enabled state, name and damper percentage."""
        await self._get(
            f"setZoneData?zone={zone_num}"
            f"&zoneSetting={1 if enabled else 0}"
            f"&name={quote(name)}"
            f"&userPercentSetting={user_percent}"
        )
