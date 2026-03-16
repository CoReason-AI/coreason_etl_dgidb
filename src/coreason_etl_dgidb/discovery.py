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
    Dynamically discovers the required DGIdb TSV dataset URLs
    by parsing the HTML of the base_url. Prioritizes defensive scraping of href
    attributes rather than relying on specific DOM text.
    Raises ConfigurationError if any required dataset is not found.
    """
    logger.info(f"Discovering DGIdb datasets from: {base_url}")

    try:
        response = requests.get(base_url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch DGIdb downloads page: {e}")
        raise ConfigurationError(f"Failed to fetch DGIdb downloads page from {base_url}") from e

    soup = BeautifulSoup(response.text, "html.parser")
    discovered_urls: dict[str, str] = {}

    # Defensive parsing: find all anchor tags with hrefs
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]

        # BeautifulSoup can return a list for some attributes, handle it safely
        href_str = href[0] if isinstance(href, list) else str(href)

        # Check if the href matches any of the required datasets
        for dataset in required_datasets:
            # We look for links that end with the dataset name (e.g. .*interactions\.tsv$)
            # Using regex for exact matching at the end of the URL path
            pattern = re.compile(rf".*{re.escape(dataset)}$")
            # We only take the first matching link for each dataset
            if pattern.search(href_str) and dataset not in discovered_urls:
                # Make sure to handle relative URLs by joining with base_url
                discovered_urls[dataset] = urljoin(base_url, href_str)
                logger.debug(f"Discovered {dataset} at {discovered_urls[dataset]}")

    # Verify that all required datasets were found
    missing_datasets = set(required_datasets) - set(discovered_urls.keys())
    if missing_datasets:
        error_msg = f"Missing required DGIdb datasets: {', '.join(missing_datasets)}"
        logger.error(error_msg)
        raise ConfigurationError(error_msg)

    logger.info(f"Successfully discovered {len(discovered_urls)} datasets.")
    return discovered_urls
