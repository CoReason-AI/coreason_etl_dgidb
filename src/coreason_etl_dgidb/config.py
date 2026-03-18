# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_dgidb

import uuid

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DGIDB_BASE_URL: str = "https://www.dgidb.org/downloads"
NAMESPACE_DGIDB: uuid.UUID = uuid.UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")


class SystemEnvironmentManifest(BaseSettings):
    """
    AGENT INSTRUCTION: This object defines the foundational environment
    configuration for the coreason_etl_dgidb pipeline. It adheres to the
    12-Factor App principles and uses strict validation to ensure all
    variables are present and correctly typed.
    """

    app_env: str = Field(
        default="development", description="The operational environment (e.g., development, testing, production)."
    )
    debug: bool = Field(default=False, description="Flag to enable or disable debug mode.")
    secret_key: str = Field(
        default="insecure_default_secret_key", description="Secret key for cryptographic signing/sessions."
    )
    log_level: str = Field(
        default="INFO", description="The minimum logging level to record (e.g., DEBUG, INFO, WARNING, ERROR)."
    )
    dgidb_base_url: str = Field(
        default=DGIDB_BASE_URL,
        description="The base URL from which DGIdb bulk files will be discovered and downloaded.",
    )
    dgidb_required_datasets: list[str] = Field(
        default_factory=lambda: ["interactions.tsv", "genes.tsv", "drugs.tsv", "categories.tsv"],
        description="The list of required DGIdb TSV datasets that must be discovered and downloaded.",
    )
    pghost: str = Field(default="localhost", description="PostgreSQL database host.")
    pgport: int = Field(default=5432, description="PostgreSQL database port.")
    pguser: str = Field(default="postgres", description="PostgreSQL database user.")
    pgpassword: str = Field(default="postgres", description="PostgreSQL database password.")
    pgdatabase: str = Field(default="postgres", description="PostgreSQL database name.")

    @property
    def postgres_dsn(self) -> str:
        """
        AGENT INSTRUCTION: Constructs the PostgreSQL connection string DSN
        based on the validated configuration attributes.
        """
        return f"postgresql://{self.pguser}:{self.pgpassword}@{self.pghost}:{self.pgport}/{self.pgdatabase}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# Instantiate a global instance to be used across the application.
config_manifest = SystemEnvironmentManifest()
