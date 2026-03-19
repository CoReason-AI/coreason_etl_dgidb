-- Copyright (c) 2026 CoReason, Inc.
--
-- This software is proprietary and dual-licensed.
-- Licensed under the Prosperity Public License 3.0 (the "License").
-- A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
-- For details, see the LICENSE file.
-- Commercial use beyond a 30-day trial requires a separate license.
--
-- Source Code: https://github.com/CoReason-AI/coreason_etl_dgidb

WITH interactions AS (
    SELECT *
    FROM {{ ref('silver_dgidb_interactions') }}
),

edges AS (
    SELECT
        coreason_id AS edge_id,
        drug_name,
        gene_symbol,
        interaction_types AS relationship_type,
        source_database,
        evidence_score
    FROM interactions
    WHERE
        drug_name IS NOT NULL
        AND gene_symbol IS NOT NULL
        AND interaction_types IS NOT NULL
)

SELECT *
FROM edges
