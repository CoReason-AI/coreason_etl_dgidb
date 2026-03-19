-- Copyright (c) 2026 CoReason, Inc.
--
-- This software is proprietary and dual-licensed.
-- Licensed under the Prosperity Public License 3.0 (the "License").
-- A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
-- For details, see the LICENSE file.
-- Commercial use beyond a 30-day trial requires a separate license.
--
-- Source Code: https://github.com/CoReason-AI/coreason_etl_dgidb

WITH edges AS (
    SELECT *
    FROM {{ ref('coreason_etl_dgidb_gold_target_edges') }}
),

-- Aggregate sources and calculate confidence based on corroborated sources and scores
high_confidence AS (
    SELECT
        drug_name,
        gene_symbol,
        relationship_type,
        COUNT(DISTINCT source_database) AS source_corroboration_count,
        MAX(evidence_score) AS max_evidence_score
    FROM edges
    GROUP BY
        drug_name,
        gene_symbol,
        relationship_type
    HAVING
        -- Example thresholds: multiple sources or high distinct evidence score
        COUNT(DISTINCT source_database) >= 2
        OR MAX(evidence_score) > 0.5
)

SELECT *
FROM high_confidence
