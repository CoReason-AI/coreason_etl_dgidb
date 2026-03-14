# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_dgidb

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    log_level: str = Field(
        default="INFO", description="The minimum logging level to record (e.g., DEBUG, INFO, WARNING, ERROR)."
    )
    dgidb_base_url: str = Field(
        default="https://www.dgidb.org/downloads",
        description="The base URL from which DGIdb bulk files will be discovered and downloaded.",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# Instantiate a global instance to be used across the application.
config_manifest = SystemEnvironmentManifest()
