# LUMC Pollentelling

Home Assistant custom integration to fetch pollen counts and history graphs from the [LUMC pollentelling](https://sec.lumc.nl/pollenwebextern/).

This integration is not affeliated, nor endorsed by LUMC, it is my own hobby project to scrape the data

Note: this scraper only extracts the total week amounts


## Features
- Sensor platform: creates a sensor for each pollen type reporting the current count.
- Camera platform: exposes a historical graph image per pollen type.

## Installation
1. Copy the `LUMC_pollentelling` directory into your Home Assistant `custom_components` folder.
2. Ensure dependencies from `manifest.json` are installed by Home Assistant (`requests`, `beautifulsoup4`).
3. Restart Home Assistant and add the integration through the UI (Configuration → Integrations).

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
