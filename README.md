# San Jac Quick Build — Snowflake Cortex Demo (Higher Ed)

**Version:** 0.6.0

Rapid demo assets for showcasing Snowflake Cortex AI capabilities at San Jacinto College (Pasadena, TX). Grounded in real SJC demographics, student lifecycle stages, program catalog, and institutional success metrics.

---

## Changelog

### v0.6.0 — 2026-04-10
- Added `docs/course-catalog.md` — 1,695 real SJC courses scraped from publications.sanjac.edu (2026-2027 catalog), including descriptions, prerequisites, credit hours, and course type; primary Cortex Search document for course/program Q&A
- Added `data/scrape_catalog.py` — scraper script that produces course-catalog.md; re-run to refresh when catalog updates

### v0.5.0 — 2026-04-09
- Corrected Cortex Code description in README — it is Snowflake's native AI coding agent (not a data generation tool)
- Added `data/generate.py` — synthetic data generation script for all 13 tables (8 dims + 5 facts)
- Added `data/requirements.txt`

### v0.4.0 — 2026-04-09
- Added `data/data-model.md` — full star schema spec with 5 fact tables, 8 dimension tables, data distributions, correlated generation rules, and metric validation targets

### v0.3.0 — 2026-04-09
- Removed `cortex/`, `streamlit/`, and `local/` scaffold folders — Cortex Code will generate these directly in Snowflake
- Updated repo structure and Quick Start accordingly

### v0.2.0 — 2026-04-09
- Added 5 parsed source documents as Markdown (brand style guide, student statistics, student success metrics, programs catalog, student lifecycle)
- Added 6 new use cases (stop-out/recruit-back, pathway completion risk, CPD workforce demand, financial aid monitoring, transfer/workforce outcomes, IR NL-to-SQL dashboard)
- Rewrote `overview.md` with real SJC context — demographics, lifecycle summary, data model notes
- Added 5 San Jacinto source PDFs to `docs/` (brand standards, statistics, student success metrics, programs & CE, TargetX student stages)

### v0.1.0 — Initial scaffold
- Repo structure, cortex setup SQL stubs, Streamlit scaffold, local dev environment
- 2 initial use cases (admissions advising chatbot, student success early-alert)
- Initial `overview.md` and `demo-script.md`

---

## Repo Structure

| Folder/File | Purpose |
|-------------|---------|
| `docs/` | Source docs, demo narrative, use-case briefs (see below) |
| `data/` | Synthetic seed data for the demo |

> Cortex Search, Cortex Analyst, and Streamlit assets are built directly in Snowflake via Cortex Code.

### docs/ Contents

| File | Description |
|------|-------------|
| `overview.md` | Demo objective, audience, data model, use case index |
| `demo-script.md` | Presenter script and talking points |
| `brand-style-guide.md` | Condensed SJC brand guide — colors, typography, voice/tone |
| `student-statistics.md` | Enrollment, demographics, and 5-year trend data |
| `student-success-metrics.md` | Entering/Continuing/Completing/Achieving metrics framework |
| `student-lifecycle.md` | TargetX student stages, Banner integration, data field mapping |
| `programs-catalog.md` | Full credit program list + CPD division by center |
| `course-catalog.md` | 1,695 real SJC courses — descriptions, prerequisites, SCH (Cortex Search source) |
| `use-cases/` | Individual use case briefs (8 total) |

### use-cases/

| File | Use Case |
|------|----------|
| `admissions-advising.md` | Admissions & enrollment advising chatbot |
| `student-success-analytics.md` | Early-alert analytics for at-risk students |
| `stop-out-recruit-back.md` | Stop-out identification and re-engagement |
| `pathway-completion-risk.md` | Pathway velocity scoring and completion risk |
| `cpd-workforce-demand.md` | CPD / workforce program demand analysis |
| `financial-aid-monitoring.md` | Financial aid gap and Pell eligibility monitoring |
| `transfer-workforce-outcomes.md` | Transfer readiness and post-graduation outcomes |
| `institutional-research-dashboard.md` | IR NL-to-SQL executive dashboard |

---

## Quick Start

### 1. Generate Synthetic Data
```bash
pip install -r data/requirements.txt
python data/generate.py
# Outputs CSVs to data/output/ — ~400K rows across 13 tables
```

### 2. Load into Snowflake
COPY INTO each table from the staged CSVs.

### 3. Build in Snowflake via Cortex Code
Cortex Code is Snowflake's native AI coding agent — it writes, debugs, and executes SQL and Python directly inside Snowflake with full schema awareness. Use it to:
- Create DDL from the data model spec
- Set up Cortex Search services over policy/catalog documents
- Build the Cortex Analyst semantic model YAML
- Scaffold the Streamlit advisor app

---

## About San Jacinto College

- **Location:** Pasadena, Texas (East Harris County / greater Houston)
- **Enrollment:** ~31,800 credit students; ~45,000 total including CPD
- **Designation:** Hispanic-Serving Institution (HSI); Aspen Institute Top 10
- **Demographics:** 63% Hispanic, 59% female, 56% Pell-eligible
- **Programs:** 200+ degrees, certificates, and CE courses across 8 areas of study
- **CRM/SIS:** TargetX (Salesforce) + Banner

---

## Tech Stack
- **Snowflake Cortex Code** — native AI coding agent; writes, debugs, and executes SQL/Python inside Snowflake with schema awareness
- **Snowflake Cortex Search** — semantic search over unstructured documents
- **Snowflake Cortex Analyst** — natural language to SQL via semantic model
- **Streamlit in Snowflake** — zero-infrastructure advisor/IR app
- **Python + Faker + pandas** — synthetic data generation (local, pre-load)
