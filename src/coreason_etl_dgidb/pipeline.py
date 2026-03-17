# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_dgidb

import dlt
from dlt.pipeline.pipeline import Pipeline

from coreason_etl_dgidb.config import config_manifest


def get_dlt_pipeline() -> Pipeline:
    """
    AGENT INSTRUCTION: Initializes and returns the dlt pipeline for the
    DGIdb ingestion process.
    Configures the pipeline to sink into PostgreSQL using the
    destination credentials from the validated configuration manifest.
    Sets the dataset schema to 'bronze'.
    """
    return dlt.pipeline(
        pipeline_name="dgidb_pipeline",
        destination="postgres",
        dataset_name="bronze",
        credentials=config_manifest.postgres_dsn,
    )
