# San Jac Quick Build — Snowflake Cortex Demo (Higher Ed)

Rapid demo assets for showcasing Snowflake Cortex capabilities at San Jacinto College.

## Repo Structure

| Folder | Purpose |
|---|---|
| `docs/` | Demo narrative, use-case briefs, and talking points (MD files) |
| `cortex/` | Snowflake Cortex Search configs, Analyst semantic models, and setup SQL |
| `streamlit/` | Streamlit in Snowflake app source |
| `local/` | Local Python dev environment — notebooks and scripts |
| `data/` | Sample / seed data for the demo |

## Quick Start

### Local Dev
```bash
cd local
pip install -r requirements.txt
cp .env.example .env   # fill in your Snowflake creds
jupyter lab
```

### Snowflake / Cortex Deployment
1. Run `cortex/sql/00_setup.sql` — creates database, warehouse, stages, roles
2. Upload source docs to the stage (`cortex/cortex_search/stage_files.sql`)
3. Create the Cortex Search service (`cortex/cortex_search/create_service.sql`)
4. Upload the semantic model YAML to the Analyst stage (`cortex/cortex_analyst/`)
5. Deploy the Streamlit app from `streamlit/` via Snowsight or SnowCLI

## Use Cases (Higher Ed Focus)
- Admissions & enrollment advising chatbot
- Financial aid Q&A over policy documents
- Course catalog semantic search
- Student success early-alert analytics

## Tech Stack
- Snowflake Cortex Search
- Snowflake Cortex Analyst (semantic model / NL-to-SQL)
- Streamlit in Snowflake
- Python / Snowpark (local notebooks)
