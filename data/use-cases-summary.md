---
title: San Jacinto College — Snowflake Cortex Demo Use Cases
---

# San Jacinto College
## Snowflake Cortex Demo — Use Case Summaries

San Jacinto College serves ~31,800 credit students in the greater Houston area. This demo applies Snowflake Cortex AI to eight real institutional workflows — from advising and early alert to workforce outcomes and executive reporting.

---

## 1. Admissions & Enrollment Advising Chatbot
**Cortex Search**

Advisors spend significant time answering repetitive questions about admission requirements, deadlines, and procedures already documented in policy docs and handbooks.

**Solution:** Cortex Search over admissions handbooks, the program catalog, and financial aid policy surfaces instant, cited answers for advisors and students via a Streamlit chatbot — no RAG plumbing, no external vector DB.

**Demo question:** *"What are the TSI requirements for enrolling in College Algebra?"*

---

## 2. Student Success Early-Alert Analytics
**Cortex Analyst**

Early identification of at-risk students relies on manual grade and attendance review — slow, inconsistent, and dependent on SQL skills most advisors don't have.

**Solution:** Cortex Analyst over structured enrollment and course-attempt data lets advisors query student performance in plain English. SJC tracks A–C success (~72% overall) and withdrawal rate (~12%) as core strategic metrics.

**Demo question:** *"Which students in MATH 1314 have below a C midterm grade and attendance under 70%?"*

---

## 3. Stop-Out & Recruit-Back Identification
**Cortex Analyst + Cortex Search**

~6% of SJC's student population is in Stop-Out status (no enrollment in 3+ terms). Another ~2% are Recruit Backs — admitted but never registered. Manual re-engagement outreach is inconsistent.

**Solution:** Cortex Analyst over TargetX stage history surfaces prioritized re-engagement lists by program area and time-out-of-enrollment. Cortex Search over advising notes adds context on why a student stopped out.

**Demo question:** *"Show me Stop-Out students who were enrolled in Health Sciences and left within the last two years."*

---

## 4. Pathway Velocity & Completion Risk Scoring
**Cortex Analyst + Snowpark ML**

SJC tracks Pathway Velocity (SCH on-path ÷ SCH required) and Pathway Consistency (% of students staying in their declared program) as strategic metrics — but computing these at scale requires SQL expertise advisors don't have.

**Solution:** Cortex Analyst exposes pathway metrics in natural language. A Snowpark ML model scores completion risk and flags off-pace students for proactive intervention before they stop out.

**Demo question:** *"Which AAS students are completing less than 60% of their required pathway credits each semester?"*

---

## 5. CPD / Workforce Program Demand Analysis
**Cortex Analyst + Cortex Search**

San Jacinto's Continuing & Professional Development division serves thousands of non-credit learners across four centers (EDGE, BIT, Corporate, Community & Health). Program managers need enrollment trends and seat utilization without SQL.

**Solution:** Cortex Analyst over CPD enrollment data lets managers self-serve on program performance. Cortex Search over course descriptions helps match students to programs by industry or skill area.

**Demo question:** *"Which CPD programs have the highest growth rate over the last two years, and where are we hitting capacity?"*

---

## 6. Financial Aid Gap & Pell Eligibility Monitoring
**Cortex Analyst + Cortex Search**

56% of SJC students are Pell-eligible. Financial barriers are a leading cause of enrollment drop-off — students in Register Pending status with no aid package are at immediate risk of losing their seat.

**Solution:** Cortex Analyst over Banner aid and enrollment data identifies students with unmet need before payment deadlines. Cortex Search over financial aid policy docs answers student and advisor questions instantly.

**Demo question:** *"How many first-term students in Register Pending status have no financial aid package this semester?"*

---

## 7. Transfer Readiness & Workforce Outcomes Tracking
**Cortex Analyst + Cortex Search**

SJC reports Transfer Rate, Transferability, Employment Rate, and Earnings after Completion to THECB — but advisors can't easily access these metrics at the program or student level without running reports.

**Solution:** Cortex Analyst over graduate outcome data lets advisors and IR staff explore outcomes by program, campus, and cohort. Cortex Search over articulation agreements answers transfer credit questions in real time.

**Demo question:** *"What is the employment rate for Process Technology graduates compared to the state benchmark?"*

---

## 8. Institutional Research NL-to-SQL Dashboard
**Cortex Analyst**

SJC's IR team produces metrics for THECB, IPEDS, the Aspen Institute, and internal SLT reporting. Building and maintaining SQL reports for each audience is slow — and non-technical leadership can't self-serve.

**Solution:** Cortex Analyst connected to the full student data warehouse gives IR analysts and executives a conversational interface over enrollment, persistence, completion, and outcome data. Generated SQL is shown alongside results for full transparency and auditability.

**Demo question:** *"What was our Fall-to-Fall persistence rate for first-time-in-college students broken down by ethnicity and Pell status?"*

---

*All Cortex Search, Cortex Analyst, and Streamlit assets are built in-platform via Snowflake Cortex Code. No external infrastructure required. All data remains inside the Snowflake perimeter.*
