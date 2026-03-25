-- Copyright (c) 2026 CoReason, Inc.
--
-- This software is proprietary and dual-licensed.
-- Licensed under the Prosperity Public License 3.0 (the "License").
-- A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
-- For details, see the LICENSE file.
-- Commercial use beyond a 30-day trial requires a separate license.
--
-- Source Code: https://github.com/CoReason-AI/coreason_etl_dgidb

WITH source AS (
    SELECT *
    FROM {{ source('bronze', 'coreason_etl_dgidb_bronze_interactions') }}
),

extracted AS (
    SELECT
        coreason_id,
        raw_data->>'drug_name' AS raw_drug_name,
        raw_data->>'drug_concept_id' AS raw_drug_concept_id,
        raw_data->>'gene_name' AS raw_gene_name,
        raw_data->>'gene_claim_name' AS raw_gene_claim_name,
        raw_data->>'interaction_types' AS raw_interaction_types,
        raw_data->>'interaction_claim_source' AS raw_interaction_claim_source,
        raw_data->>'score' AS raw_score,
        raw_data->>'evidence_score' AS raw_evidence_score
    FROM source
),

cleaned AS (
    SELECT
        coreason_id,

        -- drug_name standardization
        NULLIF(NULLIF(TRIM(COALESCE(raw_drug_name, raw_drug_concept_id)), ''), 'N/A') AS drug_name,

        -- gene_symbol standardization
        NULLIF(NULLIF(TRIM(COALESCE(raw_gene_name, raw_gene_claim_name)), ''), 'N/A') AS gene_symbol,

        -- interaction_types standardization
        NULLIF(NULLIF(TRIM(raw_interaction_types), ''), 'N/A') AS interaction_types,

        -- source_database standardization
        NULLIF(NULLIF(TRIM(raw_interaction_claim_source), ''), 'N/A') AS source_database,

        -- evidence_score casting
        CAST(
            NULLIF(NULLIF(TRIM(COALESCE(raw_score, raw_evidence_score)), ''), 'N/A')
            AS FLOAT
        ) AS evidence_score

    FROM extracted
)

SELECT
    coreason_id,
    drug_name,
    gene_symbol,
    interaction_types,
    source_database,
    evidence_score
FROM cleaned
