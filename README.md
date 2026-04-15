# ha-myair3

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A [Home Assistant](https://www.home-assistant.io/) custom integration for the **AdvantageAir MyAir3** aircon controller, installable via [HACS](https://hacs.xyz/).

---

## Features

| Entity type | What it does |
|---|---|
| **Climate** | Controls the AC unit – power, HVAC mode (cool / heat / fan only), fan speed (low / medium / high) and central target temperature |
| **Switch** | Enables or disables individual zones |
| **Sensor** | Reports measured (actual) temperature per zone and at the central unit; also shows the desired temperature for climate-controlled zones |
| **Binary sensor** | Reports low-battery warnings and motor errors for each zone |

## Requirements

- Home Assistant 2024.1 or later
- A MyAir3 controller accessible on your local network
- HACS installed in Home Assistant

## Installation

### Via HACS (recommended)

1. Open HACS in Home Assistant.
2. Click **Integrations → ⋮ → Custom repositories**.
3. Add `https://github.com/eric-winkler/ha-myair3` as an **Integration** repository.
4. Search for **MyAir3** and click **Download**.
5. Restart Home Assistant.

### Manual

Copy the `custom_components/myair3` directory into your Home Assistant
`config/custom_components/` directory and restart.

## Configuration

After installation:

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **MyAir3** and select it.
3. Enter the **IP address** (and optionally the **port**, default 80) of your
   MyAir3 controller.
4. Click **Submit** – Home Assistant will connect and create the entities.

## API notes

The MyAir3 controller exposes a plain HTTP GET API with XML responses.
Authentication uses a session cookie (password is the fixed string `password`
as set by the AdvantageAir firmware).

Key endpoints used by this integration:

| Endpoint | Description |
|---|---|
| `getSystemData` | Read AC unit state and zone count |
| `getZoneData?zone=N` | Read state for zone *N* |
| `setSystemData?…` | Update power, mode, fan speed and target temp |
| `setZoneData?zone=N&…` | Enable/disable a zone and set its damper percentage |

## Credits

- MyAir3 API reference: [eric-winkler/MyAir3Api](https://github.com/eric-winkler/MyAir3Api)
- Integration structure inspired by the built-in [Advantage Air](https://www.home-assistant.io/integrations/advantage_air/) integration in Home Assistant core
