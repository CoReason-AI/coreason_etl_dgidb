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

from coreason_etl_dgidb.main import process_dgidb_tsv


@patch("requests.get")
def test_process_dgidb_tsv_success(mock_get: MagicMock) -> None:
    """
    AGENT INSTRUCTION: Test successful processing of a DGIdb TSV file
    including identity resolution and dictionary formatting.
    """
    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"drug_name\tgene_name\n", b"Aspirin\tPTGS1\n"]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value.__enter__.return_value = mock_response

    results = list(process_dgidb_tsv("http://example.com/test.tsv", "interactions"))

    assert len(results) == 1
    row = results[0]
    assert "coreason_id" in row
    assert row["source_file_url"] == "http://example.com/test.tsv"
    assert row["raw_data"]["drug_name"] == "Aspirin"
    assert row["raw_data"]["gene_name"] == "PTGS1"


@patch("requests.get")
def test_process_dgidb_tsv_empty_file(mock_get: MagicMock) -> None:
    """
    AGENT INSTRUCTION: Ensure that empty TSV payloads are safely handled.
    """
    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"drug_name\tgene_name\n"]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value.__enter__.return_value = mock_response

    results = list(process_dgidb_tsv("http://example.com/empty.tsv", "interactions"))

    assert len(results) == 0


@patch("os.unlink")
@patch("requests.get")
def test_process_dgidb_tsv_http_error(mock_get: MagicMock, mock_unlink: MagicMock) -> None:
    """
    AGENT INSTRUCTION: Ensure that HTTP errors propagate and cleanup happens.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    mock_get.return_value.__enter__.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError):
        list(process_dgidb_tsv("http://example.com/error.tsv", "interactions"))

    # Assert cleanup happened despite the exception
    mock_unlink.assert_called_once()


@patch("requests.get")
def test_process_dgidb_tsv_nan_handling(mock_get: MagicMock) -> None:
    """
    AGENT INSTRUCTION: Ensure that missing values are mapped to None
    instead of NaN, preventing downstream JSON serialization issues.
    """
    mock_response = MagicMock()
    # Provide a blank field which Polars defaults to null/NaN
    mock_response.iter_content.return_value = [b"drug_name\tgene_name\n", b"Aspirin\t\n"]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value.__enter__.return_value = mock_response

    results = list(process_dgidb_tsv("http://example.com/nan.tsv", "interactions"))

    assert len(results) == 1
    row = results[0]
    assert row["raw_data"]["drug_name"] == "Aspirin"
    assert row["raw_data"]["gene_name"] is None
