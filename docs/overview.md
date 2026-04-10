# San Jacinto College — Snowflake Cortex Demo Overview

## About San Jacinto College

San Jacinto College is a large, diverse community college in Pasadena, Texas (East Harris County / greater Houston area), serving approximately 31,800 credit students annually plus additional CPD/non-credit learners — ~45,000 total. Founded in 1961, it is a top-10 community college (Aspen Institute) and a designated Hispanic-Serving Institution (HSI). The student body is 63% Hispanic, 59% female, and 56% Pell-eligible.

The College manages a full student lifecycle — from prospective inquiry through enrollment, persistence, graduation, and workforce placement — tracked via TargetX (Salesforce CRM) and Banner (SIS). It offers 200+ degrees and certificates across eight areas of study, plus a robust Continuing & Professional Development division reorganized in 2026 into four specialized centers.

## Demo Objective

Demonstrate Snowflake Cortex AI capabilities applied to real Higher Education workflows at San Jacinto College — showing how AI can be deployed at scale, inside the data perimeter, without external infrastructure.

## Key Capabilities to Showcase

| Capability | What It Does |
|------------|-------------|
| **Cortex Search** | Semantic search over unstructured documents (policy docs, catalog, handbooks) |
| **Cortex Analyst** | Natural language queries over structured enrollment and student success data |
| **Streamlit in Snowflake** | Zero-infrastructure AI app deployment as a unified advisor/admin interface |
| **Snowpark / Python** | Custom ML pipelines and data transformations natively in Snowflake |

## Demo Audience

- IT leadership
- Academic affairs / advising leadership
- Institutional Research / Data & Analytics team
- Student Services leadership

## Student Lifecycle Context

The demo data and use cases are grounded in San Jacinto's actual student stages (TargetX):

**Prospective → Applicant → Admitted → Eligible to Register → Enrolled → Graduate/Alumni**

with off-ramps for **Stop-Out**, **Not Interested**, and **Recruit Backs**.

Key metrics tracked across this lifecycle: pathway consistency, persistence (Fall-to-Fall, Fall-to-Spring), course success (A–C rate), withdrawal rate, time-to-degree, transfer rate, employment rate, and favorable outcomes.

## Synthetic Data Model

Demo data is generated to reflect San Jacinto's actual demographics and academic programs:
- 31,800 student records across all lifecycle stages
- Enrollment split: 34% full-time / 66% part-time
- Demographics: 63% Hispanic, 59% female, 56% Pell-eligible
- Academic programs drawn from 200+ real San Jacinto offerings across 8 areas of study and 4 CPD centers
- Metrics aligned to THECB, IPEDS, and SJC's own Strategic Measures framework

## Demo Flow

1. **Ingest** — synthetic student records, academic program catalog, and policy documents loaded into Snowflake stages
2. **Cortex Search** — semantic Q&A over the academic program catalog, handbooks, and policy docs via an advisor chatbot
3. **Cortex Analyst** — natural language enrollment and student success queries (NL → SQL → results)
4. **Streamlit App** — unified front-end for advisors and institutional research staff
5. **Governance close** — everything stays inside the Snowflake perimeter; no data leaves

## Key Use Cases

See [use-cases/](use-cases/) for full detail on each:

1. Admissions & Enrollment Advising Chatbot
2. Student Success Early-Alert Analytics
3. Stop-Out & Recruit-Back Identification
4. Pathway Velocity & Completion Risk Scoring
5. CPD / Workforce Program Demand Analysis
6. Financial Aid Gap & Pell Eligibility Monitoring
7. Transfer Readiness & University Placement Tracking
8. Institutional Research NL-to-SQL Dashboard
