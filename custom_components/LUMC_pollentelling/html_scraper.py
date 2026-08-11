# Copyright 2026 madcowGit
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

"""Helpers for scraping pollen values from the LUMC website."""

import logging
import re

import requests
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)

URL = "https://sec.lumc.nl/pollenwebextern/"


def fetch_html() -> str | None:
    """Fetch the pollen page HTML from the LUMC website."""
    try:
        resp = requests.get(URL, timeout=10)
        resp.raise_for_status()
    except requests.RequestException:
        _LOGGER.exception("Error fetching LUMC HTML")
        return None

    return resp.text


def extract_pollen_values(html: str) -> dict[str, int]:
    """Extract pollen values using the 2nd column as name and 'Totaal' as value."""
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    results: dict[str, int] = {}

    for table in tables:
        rows = table.find_all("tr")
        if not rows:
            continue

        # Convert table to matrix
        matrix = [
            [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
            for row in rows
        ]

        header = matrix[0]
        if not header:
            continue

        # Find Totaal column
        try:
            totaal_idx = next(
                i for i, h in enumerate(header) if "totaal" in h.lower()
            )
        except StopIteration:
            continue

        name_idx = 1  # ALWAYS use second column

        _LOGGER.debug(
            "Using name column index: %s, totaal index: %s",
            name_idx,
            totaal_idx,
        )

        # Extract rows
        for row in matrix[1:]:
            if len(row) <= max(name_idx, totaal_idx):
                continue

            name = row[name_idx]
            totaal_text = row[totaal_idx]

            if not name:
                continue

            match = re.search(
                r"(-?\d+)", totaal_text.replace(".", "").replace(",", "")
            )
            if not match:
                continue

            value = int(match.group(1))
            results[name] = value
            _LOGGER.debug("Extracted %s -> %s", name, value)

        if results:
            break

    if not results:
        _LOGGER.warning(
            "No pollen values found in any table with 2nd-column names"
        )

    return results
