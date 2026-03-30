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
        drug_concept_id,
        gene_name,
        gene_concept_id,
        COALESCE(interaction_types, 'unknown') AS relationship_type,
        source_database,
        evidence_score,
        is_approved,
        is_immunotherapy,
        is_anti_neoplastic
    FROM interactions
    WHERE
        -- Ensure at least one identifier exists for both nodes
        (drug_name IS NOT NULL OR drug_concept_id IS NOT NULL)
        AND (gene_name IS NOT NULL OR gene_concept_id IS NOT NULL)
)

SELECT *
FROM edges
