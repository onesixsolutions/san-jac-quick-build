-- ============================================================
-- stage_files.sql  — Upload source documents to Snowflake stage
-- Run after 00_setup.sql
-- ============================================================

USE DATABASE SAN_JAC_DEMO;
USE SCHEMA CORTEX;
USE WAREHOUSE SAN_JAC_WH;

-- Upload via SnowSQL CLI:
--   PUT file:///path/to/your/docs/*.pdf @DOCS_STAGE AUTO_COMPRESS=FALSE;
-- Or use Snowsight: Data > Stages > DOCS_STAGE > + Files

-- Verify staged files
LIST @DOCS_STAGE;

-- Parse text from staged documents (requires Cortex PARSE_DOCUMENT)
CREATE OR REPLACE TABLE CORTEX.DOCS_PARSED AS
SELECT
    RELATIVE_PATH AS file_name,
    SNOWFLAKE.CORTEX.PARSE_DOCUMENT(
        @DOCS_STAGE,
        RELATIVE_PATH,
        {'mode': 'LAYOUT'}
    ):content::STRING AS content
FROM DIRECTORY(@DOCS_STAGE)
WHERE RELATIVE_PATH ILIKE '%.pdf'
   OR RELATIVE_PATH ILIKE '%.txt'
   OR RELATIVE_PATH ILIKE '%.md';
