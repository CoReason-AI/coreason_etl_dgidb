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
from pathlib import Path


def test_logger_directory_creation() -> None:
    """
    AGENT INSTRUCTION: Ensure that log directory is correctly checked.
    """
    from coreason_etl_dgidb.utils.logger import log_path

    assert log_path.exists()


def test_logger_directory_does_not_exist(tmp_path: Path) -> None:
    """
    AGENT INSTRUCTION: Test the creation of the log directory if it does not exist.
    """
    import importlib

    # We override the Path used in logger module locally using monkeypatch or mock.
    # But testing module-level path creation is tricky with reload. Let's just create
    # a temporary directory, delete it, monkeypatch logger.Path to use it, and reload.
    import coreason_etl_dgidb.utils.logger as logger_module

    # Change current working directory to tmp_path temporarily
    old_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        # Before reload, the "logs" dir should not exist in the temp dir
        assert not Path("logs").exists()

        importlib.reload(logger_module)

        # After reload, the "logs" dir should be created
        assert Path("logs").exists()
    finally:
        os.chdir(old_cwd)
