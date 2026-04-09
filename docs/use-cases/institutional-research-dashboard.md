# Use Case: Institutional Research NL-to-SQL Dashboard

## Problem
San Jacinto's Institutional Research (IR) team produces strategic metrics for THECB, IPEDS, the Aspen Institute rankings, and internal SLT reporting — covering enrollment, persistence, completion, transfer, and workforce outcomes across a 31,800-student population. Building and maintaining custom SQL reports for each audience is slow, and non-technical stakeholders (deans, VPs, board members) can't self-serve on data questions.

## Solution
Cortex Analyst connected to the full student data warehouse gives IR analysts and leadership a natural language interface over structured enrollment, performance, and outcome data. The Streamlit app serves as an executive dashboard with conversational drill-down. All queries are transparent (generated SQL is shown alongside results).

## Demo Questions (Cortex Analyst)
- "What was our Fall-to-Fall persistence rate for first-time-in-college students last year?"
- "How does our 3-year graduation rate compare across our five campuses?"
- "Show me Favorable Outcomes by program area for the 2023–24 cohort"
- "What is the A–C success rate for Hispanic female students in STEM courses?"
- "Which programs have the highest withdrawal rates and what is the trend over three years?"
- "Break down enrollment by full-time vs. part-time status and Pell eligibility"

## Data Sources
- Banner SIS: enrollment, grades, withdrawals, academic profiles
- TargetX: student stage history and persistence tracking
- THECB / IPEDS reporting datasets
- Credential award and outcome records

## Key Metrics Surfaced
Per the SJC Strategic Measures framework:
- Admissions-to-Enrollment Efficiency
- Fall-to-Fall and Fall-to-Spring Persistence
- A–C Course Success Rate
- Graduation Rate (2-yr, 3-yr, 4-yr) by cohort
- Degrees/Certificates Awarded (total and in critical fields)
- Favorable Outcomes
- Transfer Rate and Transferability
- Employment Rate and Earnings after Completion

## Expected Outcome
- IR team reduces time spent on ad hoc SQL requests
- Non-technical leadership can explore data conversationally
- Generated SQL is auditable and reusable
- Consistent metric definitions across all audiences (board, SLT, THECB)
