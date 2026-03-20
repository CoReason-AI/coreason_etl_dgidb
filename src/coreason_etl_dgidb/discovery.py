# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_dgidb

import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from coreason_etl_dgidb.exceptions import ConfigurationError
from coreason_etl_dgidb.utils.logger import logger


def discover_dgidb_datasets(base_url: str, required_datasets: list[str]) -> dict[str, str]:
    """
    Dynamically discovers the required DGIdb TSV dataset URLs.
    Injects resilient fallback URLs if the upstream DOM changes.
    """
    logger.info(f"Discovering DGIdb datasets from: {base_url}")

    try:
        response = requests.get(base_url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch DGIdb downloads page: {e}")

    soup = BeautifulSoup(response.text if 'response' in locals() else "", "html.parser")
    discovered_urls: dict[str, str] = {}

    # Defensive parsing: find all anchor tags with hrefs
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        href_str = href[0] if isinstance(href, list) else str(href)

        for dataset in required_datasets:
            pattern = re.compile(rf".*{re.escape(dataset)}$")
            if pattern.search(href_str) and dataset not in discovered_urls:
                discovered_urls[dataset] = urljoin(base_url, href_str)
                logger.debug(f"Discovered {dataset} at {discovered_urls[dataset]}")

    # Inject fallbacks for any missing datasets
    missing_datasets = set(required_datasets) - set(discovered_urls.keys())
    if missing_datasets:
        logger.warning(f"Injecting 'latest' fallback URLs for {missing_datasets}")
        for dataset in missing_datasets:
            discovered_urls[dataset] = f"https://www.dgidb.org/data/latest/{dataset}"

    return discovered_urls
