# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_dgidb

import pytest

from coreason_etl_dgidb.exceptions import ConfigurationError


def test_configuration_error_instantiation() -> None:
    """
    AGENT INSTRUCTION: Ensure that ConfigurationError can be instantiated
    and raised properly with a message.
    """
    error_msg = "Required TSV link not found."
    with pytest.raises(ConfigurationError) as exc_info:
        raise ConfigurationError(error_msg)

    assert str(exc_info.value) == error_msg
