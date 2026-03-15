# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_dgidb

from unittest.mock import MagicMock, patch

import pytest
import requests

from coreason_etl_dgidb.discovery import discover_dgidb_datasets
from coreason_etl_dgidb.exceptions import ConfigurationError


@patch("requests.get")
def test_discover_dgidb_datasets_success(mock_get: MagicMock) -> None:
    """
    Ensure that required datasets are discovered
    correctly when proper HTML containing matching hrefs is provided.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = """
        <html>
            <body>
                <a href="/downloads/v2023-01-01/interactions.tsv">Download Interactions</a>
                <a href="https://example.com/downloads/v2023/genes.tsv">Genes File</a>
                <a href="drugs.tsv">Drugs Data</a>
                <a href="/other/categories.tsv">Categories</a>
            </body>
        </html>
    """
    mock_get.return_value = mock_response

    base_url = "https://www.dgidb.org/downloads"
    required = ["interactions.tsv", "genes.tsv", "drugs.tsv", "categories.tsv"]

    discovered = discover_dgidb_datasets(base_url, required)

    assert len(discovered) == 4
    assert discovered["interactions.tsv"] == "https://www.dgidb.org/downloads/v2023-01-01/interactions.tsv"
    assert discovered["genes.tsv"] == "https://example.com/downloads/v2023/genes.tsv"
    assert discovered["drugs.tsv"] == "https://www.dgidb.org/drugs.tsv"
    assert discovered["categories.tsv"] == "https://www.dgidb.org/other/categories.tsv"


@patch("requests.get")
def test_discover_dgidb_datasets_missing_required(mock_get: MagicMock) -> None:
    """
    Verify that a ConfigurationError is raised when
    not all required datasets are discovered in the HTML.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = """
        <html>
            <body>
                <a href="/downloads/v2023-01-01/interactions.tsv">Download Interactions</a>
                <a href="genes.tsv">Genes</a>
                <!-- Missing drugs.tsv and categories.tsv -->
            </body>
        </html>
    """
    mock_get.return_value = mock_response

    base_url = "https://www.dgidb.org/downloads"
    required = ["interactions.tsv", "genes.tsv", "drugs.tsv", "categories.tsv"]

    with pytest.raises(ConfigurationError, match=r"Missing required DGIdb datasets: .*"):
        discover_dgidb_datasets(base_url, required)


@patch("requests.get")
def test_discover_dgidb_datasets_http_error(mock_get: MagicMock) -> None:
    """
    Verify that HTTP errors encountered during
    the HTML fetch surface a ConfigurationError.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    mock_get.return_value = mock_response

    base_url = "https://www.dgidb.org/downloads"
    required = ["interactions.tsv"]

    with pytest.raises(ConfigurationError, match="Failed to fetch DGIdb downloads page"):
        discover_dgidb_datasets(base_url, required)


@patch("requests.get")
def test_discover_dgidb_datasets_ignore_non_matching(mock_get: MagicMock) -> None:
    """
    Ensure that irrelevant hrefs are ignored and only
    the required ones are processed and correctly joined to the base url.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = """
        <html>
            <body>
                <a href="/random/link.pdf">PDF Document</a>
                <a href="http://other.org/file.txt">Text File</a>
                <a href="/some/path/interactions.tsv">Interactions</a>
            </body>
        </html>
    """
    mock_get.return_value = mock_response

    base_url = "https://www.dgidb.org/downloads"
    required = ["interactions.tsv"]

    discovered = discover_dgidb_datasets(base_url, required)

    assert len(discovered) == 1
    assert "interactions.tsv" in discovered
    assert discovered["interactions.tsv"] == "https://www.dgidb.org/some/path/interactions.tsv"
