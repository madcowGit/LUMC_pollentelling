# LUMC Pollentelling

Home Assistant custom integration to fetch pollen counts and history graphs from the [LUMC pollentelling](https://sec.lumc.nl/pollenwebextern/).

This integration is not affeliated, nor endorsed by LUMC, it is my own hobby project to scrape the data

Note: this scraper only extracts the total week amounts


## Features
- Sensor platform: creates a sensor for each pollen type reporting the current count.
- Camera platform: exposes a historical graph image per pollen type.

## Installation
###HACS (as a custom repository)
In Home Assistant, open HACS → Integrations.
Click ⋯ (three dots) → Custom repositories.
Paste https://github.com/madcowGit/LUMC_pollentelling and select Type: Integration, then click Add.
Back in HACS, search for LUMC (custom component) and click Install.
Restart Home Assistant when prompted.
###Manual
Copy the custom_components/gluetun_cc/ directory into your HA config/custom_components/ and restart.

## Configuration
The integration exposes a single option in the config flow:

- `cache_ttl` (integer, default: 3600): number of seconds to cache fetched pollen data and images.

No YAML configuration is required — configuration is done via the UI.

## Testing
Run the included unit tests from the repository root (requires a Python test runner such as `pytest`):

```bash
pip install -r requirements.txt
pytest -q
```

## License
See the repository `LICENSE` file for licensing information.
