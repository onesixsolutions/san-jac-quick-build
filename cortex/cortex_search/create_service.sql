-- ============================================================
-- create_service.sql  — Create Cortex Search service
-- Run after stage_files.sql and docs are parsed
-- ============================================================

USE DATABASE SAN_JAC_DEMO;
USE SCHEMA CORTEX;
USE WAREHOUSE SAN_JAC_WH;

CREATE OR REPLACE CORTEX SEARCH SERVICE SAN_JAC_DOCS_SEARCH
  ON content
  ATTRIBUTES file_name
  WAREHOUSE = SAN_JAC_WH
  TARGET_LAG = '1 hour'
  AS (
    SELECT file_name, content
    FROM CORTEX.DOCS_PARSED
  );

-- Test the service
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'SAN_JAC_DEMO.CORTEX.SAN_JAC_DOCS_SEARCH',
    'What are the financial aid appeal requirements?',
    {}
);
