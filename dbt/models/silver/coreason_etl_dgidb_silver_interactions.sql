-- Copyright (c) 2026 CoReason, Inc.
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
        raw_data->>'gene_concept_id' AS raw_gene_concept_id,
        raw_data->>'gene_claim_name' AS raw_gene_claim_name,
        raw_data->>'interaction_types' AS raw_interaction_types,
        raw_data->>'interaction_claim_source' AS raw_interaction_claim_source,
        raw_data->>'score' AS raw_score,
        raw_data->>'evidence_score' AS raw_evidence_score,
        
        -- New clinical flags extracted
        raw_data->>'approved' AS raw_approved,
        raw_data->>'immunotherapy' AS raw_immunotherapy,
        raw_data->>'anti_neoplastic' AS raw_anti_neoplastic
    FROM source
),

cleaned AS (
    SELECT
        coreason_id,

        -- Keep names and IDs separated
        NULLIF(NULLIF(TRIM(raw_drug_name), ''), 'N/A') AS drug_name,
        NULLIF(NULLIF(TRIM(raw_drug_concept_id), ''), 'N/A') AS drug_concept_id,

        -- Extract gene name/symbol and ID separately
        NULLIF(NULLIF(TRIM(COALESCE(raw_gene_name, raw_gene_claim_name)), ''), 'N/A') AS gene_name,
        NULLIF(NULLIF(TRIM(raw_gene_concept_id), ''), 'N/A') AS gene_concept_id,

        NULLIF(NULLIF(TRIM(raw_interaction_types), ''), 'N/A') AS interaction_types,
        NULLIF(NULLIF(TRIM(raw_interaction_claim_source), ''), 'N/A') AS source_database,

        CAST(
            NULLIF(NULLIF(TRIM(COALESCE(raw_score, raw_evidence_score)), ''), 'N/A')
            AS FLOAT
        ) AS evidence_score,

        -- Cast clinical flags to boolean safely (Handling literal 'NULL' strings)
        CAST(NULLIF(NULLIF(UPPER(TRIM(raw_approved)), 'NULL'), '') AS BOOLEAN) AS is_approved,
        CAST(NULLIF(NULLIF(UPPER(TRIM(raw_immunotherapy)), 'NULL'), '') AS BOOLEAN) AS is_immunotherapy,
        CAST(NULLIF(NULLIF(UPPER(TRIM(raw_anti_neoplastic)), 'NULL'), '') AS BOOLEAN) AS is_anti_neoplastic

    FROM extracted
)

SELECT
    coreason_id,
    drug_name,
    drug_concept_id,
    gene_name,
    gene_concept_id,
    interaction_types,
    source_database,
    evidence_score,
    is_approved,
    is_immunotherapy,
    is_anti_neoplastic
FROM cleaned
