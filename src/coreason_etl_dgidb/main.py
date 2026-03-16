# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_dgidb

import os
import tempfile
import uuid
from collections.abc import Iterator
from typing import Any

import polars as pl
import requests

from coreason_etl_dgidb.utils.logger import logger

NAMESPACE_DGIDB = uuid.UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")


def process_dgidb_tsv(url: str, file_type: str) -> Iterator[dict[str, Any]]:
    """
    AGENT INSTRUCTION: This capability fetches, processes, and yields
    DGIdb bulk TSV files safely from disk.
    It guarantees that `max_table_nesting=0` in dlt will not result in
    schema shredding by yielding a dict with `raw_data`.
    """
    # file_type is deliberately included in the signature for logging or future branching
    logger.debug(f"Processing DGIdb TSV dataset: {file_type} from {url}")

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".tsv")  # noqa: SIM115
    try:
        # 1. Stream to fast NVMe disk to prevent OOM
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
        tmp_file.close()  # Release OS lock

        # 2. Read from disk using Polars
        df = pl.read_csv(tmp_file.name, separator="\t", infer_schema_length=10000)

        # 3. Handle Float NaN vs Null serialization trap (Polars safety)
        # Note: In polars >= 1.0, `.fill_null(None)` is not valid.
        # We'll use `.fill_nan(None)` for floats, and let Polars treat standard nulls correctly.
        df = df.fill_nan(None)

        # 4. Shift-Left UUIDv5 Generation
        # Hash the entire row string representation for a unique ID per distinct record
        df = df.with_columns(
            pl.concat_str(pl.all())
            .map_batches(
                lambda s: pl.Series([str(uuid.uuid5(NAMESPACE_DGIDB, str(x))) if x else None for x in s]),
                return_dtype=pl.String,
            )
            .alias("coreason_id")
        )

        # 5. Prevent dlt Schema Shredding by wrapping in raw_data
        for row in df.to_dicts():
            yield {
                "coreason_id": row.get("coreason_id"),
                "source_file_url": url,
                "raw_data": {k: v for k, v in row.items() if k != "coreason_id"},
            }

    finally:
        os.unlink(tmp_file.name)  # Cross-platform cleanup
