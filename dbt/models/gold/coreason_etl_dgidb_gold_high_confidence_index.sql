-- Copyright (c) 2026 CoReason, Inc.
-- Source Code: https://github.com/CoReason-AI/coreason_etl_dgidb

WITH edges AS (
    SELECT *
    FROM {{ ref('coreason_etl_dgidb_gold_target_edges') }}
),

high_confidence AS (
    SELECT
        drug_name,
        drug_concept_id,
        gene_name,
        gene_concept_id,
        relationship_type,
        COUNT(*) AS total_evidence_records,
        MAX(evidence_score) AS max_evidence_score
    FROM edges
    GROUP BY
        drug_name,
        drug_concept_id,
        gene_name,
        gene_concept_id,
        relationship_type
)

SELECT *
FROM high_confidence
