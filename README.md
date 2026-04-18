# MyAir3 Integration

This integration exposes the aircon sensors and functions made available by Advantage Air MyAir3 controllers over http to Home Assistant.

[![GitHub release](https://img.shields.io/github/release/eric-winkler/ha-myair3.svg)](https://github.com/eric-winkler/ha-myair3/releases/)
[![HACS Validation](https://github.com/eric-winkler/ha-myair3/actions/workflows/validate.yml/badge.svg)](https://github.com/eric-winkler/ha-myair3/actions/workflows/validate.yml)
[![Tests](https://github.com/eric-winkler/ha-myair3/actions/workflows/tests.yml/badge.svg)](https://github.com/eric-winkler/ha-myair3/actions/workflows/tests.yml)

## Screenshots

![Overall functionality](docs/images/myair3-screenshot.png)


## Installation

1. Install this integration with HACS

   [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=eric-winkler&repository=ha-myair3&category=integration)

1. Restart HA
1. Start the configuration flow:

   [![Start Config Flow](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=myair3)

   Or: Go to `Configuration` -> `Integrations` and click the `+ Add Integration`. Select `MyAir3` from the list

1. Specify the IP address of your MyAir3 controller
