# coreason_etl_dgidb

ETL pipeline for extracting and processing DGIdb drug-gene interaction data.

[![CI/CD](https://github.com/CoReason-AI/coreason_etl_dgidb/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/CoReason-AI/coreason_etl_dgidb/actions/workflows/ci-cd.yml)
[![PyPI](https://img.shields.io/pypi/v/coreason_etl_dgidb.svg)](https://pypi.org/project/coreason_etl_dgidb/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/coreason_etl_dgidb.svg)](https://pypi.org/project/coreason_etl_dgidb/)
[![License](https://img.shields.io/github/license/CoReason-AI/coreason_etl_dgidb)](https://github.com/CoReason-AI/coreason_etl_dgidb/blob/main/LICENSE)
[![Codecov](https://codecov.io/gh/CoReason-AI/coreason_etl_dgidb/branch/main/graph/badge.svg)](https://codecov.io/gh/CoReason-AI/coreason_etl_dgidb)
[![Downloads](https://static.pepy.tech/badge/coreason_etl_dgidb)](https://pepy.tech/project/coreason_etl_dgidb)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

## Getting Started

### Prerequisites

- Python 3.14+
- uv

### Installation

1.  Clone the repository:
    ```sh
    git clone https://github.com/CoReason-AI/coreason_etl_dgidb.git
    cd coreason_etl_dgidb
    ```
2.  Install dependencies:
    ```sh
    uv sync --all-extras --dev
    ```

### Usage

-   Run the linter:
    ```sh
    uv run pre-commit run --all-files
    ```
-   Run the tests:
    ```sh
    uv run pytest
    ```

## End-to-End Local Testing (PostgreSQL)

You can run the entire ETL pipeline locally on your machine without Docker. The pipeline relies entirely on the local `uv` virtual environment and an existing PostgreSQL instance.

### Data Source & Size
- **Source Link:** Data is dynamically discovered and scraped from [https://www.dgidb.org/downloads](https://www.dgidb.org/downloads).
- **Size:** The downloaded TSVs (interactions, genes, drugs, categories) total approximately **10-15 MB** locally compressed, and will expand into structured JSONB rows and standardized Medallion tables in Postgres.

### 1. Database Setup
Create a target database in your local PostgreSQL instance:
```sh
createdb dgidb_test
```

### 2. Configure Environment
Set the required environment variables to point `dlt` and `dbt` to your database. You can export these in your shell or use a `.env` file at the root of the project:
```sh
export PGHOST=localhost
export PGPORT=5432
export PGUSER=postgres      # Replace with your postgres username
export PGPASSWORD=postgres  # Replace with your postgres password
export PGDATABASE=dgidb_test
```

### 3. Run Bronze Layer Ingestion (`dlt`)
Use the included `run_pipeline.py` entry point to execute the Python `dlt` ingestion. This scrapes the URLs, downloads the data to a memory-safe temporary file, generates UUIDv5s using `polars`, and loads the JSONB rows into your `bronze` schema.
```sh
uv run python run_pipeline.py
```

### 4. Run Silver & Gold Transformations (`dbt`)
Once the Bronze layer is populated, use `dbt` to perform data cleaning (Silver) and graph edge generation (Gold) fully in-database.
```sh
cd dbt
uv run dbt deps
uv run dbt build
```

### 5. Verify the Results
You can query the final analytical tables directly via `psql` or any SQL client:
```sh
psql -d dgidb_test
```
```sql
-- Check the structured Gold graph edges
SELECT * FROM gold.coreason_etl_dgidb_gold_target_edges LIMIT 10;

-- Check the high-confidence RAG index
SELECT * FROM gold.coreason_etl_dgidb_gold_high_confidence_index LIMIT 10;
```
