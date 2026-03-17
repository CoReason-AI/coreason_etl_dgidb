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

from coreason_etl_dgidb.config import config_manifest
from coreason_etl_dgidb.pipeline import get_dlt_pipeline


@patch("dlt.pipeline")
def test_get_dlt_pipeline(mock_pipeline: MagicMock) -> None:
    """
    AGENT INSTRUCTION: Ensures the dlt pipeline is instantiated with the
    correct configuration parameters mapped from the environment manifest.
    """
    # Act
    get_dlt_pipeline()

    # Assert
    mock_pipeline.assert_called_once()
    kwargs = mock_pipeline.call_args.kwargs
    assert kwargs["pipeline_name"] == "dgidb_pipeline"
    assert kwargs["dataset_name"] == "bronze"
    # Destination is now a Destination object
    assert kwargs["destination"].destination_type in ("postgres", "dlt.destinations.postgres")
    assert kwargs["destination"].config_params["credentials"] == config_manifest.postgres_dsn
