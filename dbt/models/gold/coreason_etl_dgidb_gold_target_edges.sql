-- Copyright (c) 2026 CoReason, Inc.
-- Source Code: https://github.com/CoReason-AI/coreason_etl_dgidb

WITH interactions AS (
    SELECT *
    FROM {{ ref('coreason_etl_dgidb_silver_interactions') }}
),

edges AS (
    SELECT
        coreason_id AS edge_id,
        drug_name,
        gene_symbol,
        COALESCE(interaction_types, 'unknown') AS relationship_type,
        source_database,
        evidence_score
    FROM interactions
    WHERE
        drug_name IS NOT NULL
        AND gene_symbol IS NOT NULL
)

SELECT *
FROM edges
