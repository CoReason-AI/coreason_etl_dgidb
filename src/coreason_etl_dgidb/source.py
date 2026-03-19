# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_dgidb

from collections.abc import Iterator
from typing import Any

import dlt

from coreason_etl_dgidb.config import config_manifest
from coreason_etl_dgidb.discovery import discover_dgidb_datasets
from coreason_etl_dgidb.main import process_dgidb_tsv
from coreason_etl_dgidb.utils.logger import logger


@dlt.source(max_table_nesting=0)  # type: ignore[misc]
def dgidb_source() -> Iterator[Any]:
    """
    AGENT INSTRUCTION: This capability acts as the dlt source for the DGIdb datasets.
    It orchestrates discovery of required TSV URLs and creates a distinct dlt.resource
    for each required dataset to load it safely into PostgreSQL.
    """
    logger.info("Initializing DGIdb dlt source extraction")
    discovered_urls = discover_dgidb_datasets(
        base_url=config_manifest.dgidb_base_url,
        required_datasets=config_manifest.dgidb_required_datasets,
    )

    for dataset_name, url in discovered_urls.items():
        # Derive the table name from the dataset file name, e.g., interactions.tsv -> dgidb_interactions_raw
        table_suffix = dataset_name.replace(".tsv", "")
        table_name = f"dgidb_{table_suffix}_raw"

        @dlt.resource(name=table_name, write_disposition="replace")  # type: ignore[misc]
        def dataset_resource(dataset_url: str = url, type_name: str = table_suffix) -> Iterator[dict[str, Any]]:
            yield from process_dgidb_tsv(dataset_url, type_name)

        yield dataset_resource
