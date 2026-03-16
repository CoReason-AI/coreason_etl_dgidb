# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_dgidb

from pathlib import Path

import yaml


def test_dbt_schema_exists_and_valid() -> None:
    """
    AGENT INSTRUCTION: Programmatically verify that the required
    dbt schema.yml exists and contains the strict data tests.
    """
    schema_path = Path("dbt/models/schema.yml")
    assert schema_path.exists(), "dbt/models/schema.yml does not exist."

    with open(schema_path) as f:
        schema = yaml.safe_load(f)

    assert "models" in schema, "schema.yml missing 'models' key."

    # Find the target model
    interactions_model = next((m for m in schema["models"] if m.get("name") == "silver_dgidb_interactions"), None)
    assert interactions_model is not None, "Model 'silver_dgidb_interactions' not found in schema.yml."

    columns = {col["name"]: col for col in interactions_model.get("columns", [])}

    # Check drug_name tests
    assert "drug_name" in columns, "Column 'drug_name' not found."
    drug_name_tests = columns["drug_name"].get("tests", [])
    has_not_null_drug = any(
        isinstance(t, dict)
        and "not_null" in t
        and isinstance(t["not_null"], dict)
        and t["not_null"].get("config", {}).get("severity") == "warn"
        for t in drug_name_tests
    )
    assert has_not_null_drug, "Strict 'not_null' test with 'severity: warn' missing for 'drug_name'."

    # Check gene_symbol tests
    assert "gene_symbol" in columns, "Column 'gene_symbol' not found."
    gene_symbol_tests = columns["gene_symbol"].get("tests", [])
    has_not_null_gene = any(
        isinstance(t, dict)
        and "not_null" in t
        and isinstance(t["not_null"], dict)
        and t["not_null"].get("config", {}).get("severity") == "warn"
        for t in gene_symbol_tests
    )
    assert has_not_null_gene, "Strict 'not_null' test with 'severity: warn' missing for 'gene_symbol'."
