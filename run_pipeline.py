# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_dgidb

"""
Entry point script for local end-to-end testing of the Bronze layer ingestion.
This script orchestrates the dlt pipeline extraction and loads the discovered
DGIdb bulk files into PostgreSQL.
"""

from coreason_etl_dgidb.pipeline import get_dlt_pipeline
from coreason_etl_dgidb.source import dgidb_source
from coreason_etl_dgidb.utils.logger import logger

if __name__ == "__main__":
    logger.info("Initializing local DGIdb ingestion pipeline...")

    # Instantiate the Postgres destination dlt pipeline
    pipeline = get_dlt_pipeline()

    # Run the source through the pipeline to extract and load to the Bronze layer
    load_info = pipeline.run(dgidb_source())

    logger.info("Pipeline execution completed successfully.")
    print(load_info)
