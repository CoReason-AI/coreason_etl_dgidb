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
from unittest.mock import patch

from coreason_etl_dgidb.config import SystemEnvironmentManifest


@patch.dict(os.environ, {}, clear=True)
def test_system_environment_manifest_defaults() -> None:
    """
    AGENT INSTRUCTION: Ensure that the default values are instantiated correctly
    when no environment variables are present.
    """
    manifest = SystemEnvironmentManifest()
    assert manifest.app_env == "development"
    assert manifest.debug is False
    assert manifest.log_level == "INFO"
    assert manifest.dgidb_base_url == "https://www.dgidb.org/downloads"
    assert manifest.dgidb_required_datasets == ["interactions.tsv", "genes.tsv", "drugs.tsv", "categories.tsv"]
    assert manifest.pghost == "localhost"
    assert manifest.pgport == 5432
    assert manifest.pguser == "postgres"
    assert manifest.pgpassword == "postgres"
    assert manifest.pgdatabase == "postgres"


@patch.dict(
    os.environ,
    {
        "APP_ENV": "production",
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
        "DGIDB_BASE_URL": "https://example.com/downloads",
        "DGIDB_REQUIRED_DATASETS": '["dataset1.tsv","dataset2.tsv"]',
    },
)
def test_system_environment_manifest_overrides() -> None:
    """
    AGENT INSTRUCTION: Ensure that environment variables correctly override the
    default configuration values.
    """
    manifest = SystemEnvironmentManifest()
    assert manifest.app_env == "production"
    assert manifest.debug is True
    assert manifest.log_level == "DEBUG"
    assert manifest.dgidb_base_url == "https://example.com/downloads"
    assert manifest.dgidb_required_datasets == ["dataset1.tsv", "dataset2.tsv"]


@patch.dict(os.environ, {"DEBUG": "False"})
def test_system_environment_manifest_debug_override_false() -> None:
    """
    AGENT INSTRUCTION: Test explicit setting of False to the boolean debug flag.
    """
    manifest = SystemEnvironmentManifest()
    assert manifest.debug is False


@patch.dict(
    os.environ,
    {
        "PGHOST": "test_host",
        "PGPORT": "5433",
        "PGUSER": "test_user",
        "PGPASSWORD": "test_password",
        "PGDATABASE": "test_db",
    },
)
def test_system_environment_manifest_postgres_overrides() -> None:
    """
    AGENT INSTRUCTION: Ensure that environment variables correctly override the
    default configuration values for Postgres.
    """
    manifest = SystemEnvironmentManifest()
    assert manifest.pghost == "test_host"
    assert manifest.pgport == 5433
    assert manifest.pguser == "test_user"
    assert manifest.pgpassword == "test_password"
    assert manifest.pgdatabase == "test_db"


@patch.dict(os.environ, {}, clear=True)
def test_system_environment_manifest_postgres_dsn_default() -> None:
    """
    AGENT INSTRUCTION: Ensure the default computed postgres_dsn is correct.
    """
    manifest = SystemEnvironmentManifest()
    assert manifest.postgres_dsn == "postgresql://postgres:postgres@localhost:5432/postgres"


@patch.dict(
    os.environ,
    {
        "PGHOST": "db.example.com",
        "PGPORT": "5432",
        "PGUSER": "admin",
        "PGPASSWORD": "secretpassword",
        "PGDATABASE": "prod_db",
    },
)
def test_system_environment_manifest_postgres_dsn_override() -> None:
    """
    AGENT INSTRUCTION: Ensure the computed postgres_dsn updates correctly with env overrides.
    """
    manifest = SystemEnvironmentManifest()
    assert manifest.postgres_dsn == "postgresql://admin:secretpassword@db.example.com:5432/prod_db"
