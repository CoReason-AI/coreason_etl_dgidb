# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_dgidb

import collections.abc
from unittest.mock import MagicMock, call, patch

import pytest

from coreason_etl_dgidb.exceptions import ConfigurationError
from coreason_etl_dgidb.source import dgidb_source


@patch("coreason_etl_dgidb.source.process_dgidb_tsv")
@patch("coreason_etl_dgidb.source.discover_dgidb_datasets")
def test_dgidb_source(mock_discover: MagicMock, mock_process: MagicMock) -> None:
    """
    AGENT INSTRUCTION: Ensure the dlt source is correctly configured,
    calls discovery, and yields dlt.resource functions for each configured dataset.
    """
    mock_discover.return_value = {
        "interactions.tsv": "http://example.com/interactions.tsv",
        "genes.tsv": "http://example.com/genes.tsv",
    }

    # Process should yield a single dict mock
    mock_process.return_value = iter([{"coreason_id": "123", "raw_data": {"a": 1}}])

    source = dgidb_source()

    # The source should yield two resource decorators
    resources = list(source.resources.values())
    assert len(resources) == 2

    res_interactions = resources[0]
    res_genes = resources[1]

    assert res_interactions.name == "coreason_etl_dgidb_bronze_interactions"
    assert res_genes.name == "coreason_etl_dgidb_bronze_genes"

    # Execution check for the resource inner generator
    # resources are generators when called
    res_iter = iter(res_interactions)
    assert isinstance(res_iter, collections.abc.Iterator)

    first_row = next(res_iter)
    assert first_row == {"coreason_id": "123", "raw_data": {"a": 1}}

    # Verify process_dgidb_tsv was correctly orchestrated
    mock_process.assert_called_once_with("http://example.com/interactions.tsv", "interactions")


@patch("coreason_etl_dgidb.source.process_dgidb_tsv")
@patch("coreason_etl_dgidb.source.discover_dgidb_datasets")
def test_dgidb_source_closure_binding(mock_discover: MagicMock, mock_process: MagicMock) -> None:
    """
    AGENT INSTRUCTION: Complex scenario test to ensure that the python closure late-binding
    loop bug is avoided, meaning each resource holds on to its correct respective url and type.
    """
    mock_discover.return_value = {
        "dataset_a.tsv": "http://a.com/data.tsv",
        "dataset_b.tsv": "http://b.com/data.tsv",
        "dataset_c.tsv": "http://c.com/data.tsv",
    }
    mock_process.return_value = iter([])

    source = dgidb_source()
    resources = list(source.resources.values())

    assert len(resources) == 3

    # Force evaluation of all resources to see what process_dgidb_tsv gets called with
    for res in resources:
        list(iter(res))

    # Expect exactly three distinct calls
    expected_calls = [
        call("http://a.com/data.tsv", "dataset_a"),
        call("http://b.com/data.tsv", "dataset_b"),
        call("http://c.com/data.tsv", "dataset_c"),
    ]

    mock_process.assert_has_calls(expected_calls, any_order=True)
    assert mock_process.call_count == 3


@patch("coreason_etl_dgidb.source.discover_dgidb_datasets")
def test_dgidb_source_discovery_failure(mock_discover: MagicMock) -> None:
    """
    AGENT INSTRUCTION: Edge case where discovery fails natively.
    Ensure exception propagates.
    """
    mock_discover.side_effect = ConfigurationError("Failed to fetch DGIdb downloads page")

    with pytest.raises(ConfigurationError):
        dgidb_source()


@patch("coreason_etl_dgidb.source.discover_dgidb_datasets")
def test_dgidb_source_empty_discovery(mock_discover: MagicMock) -> None:
    """
    AGENT INSTRUCTION: Edge case where discovery succeeds but returns no datasets.
    """
    mock_discover.return_value = {}

    source = dgidb_source()
    resources = list(source.resources.values())

    assert len(resources) == 0
