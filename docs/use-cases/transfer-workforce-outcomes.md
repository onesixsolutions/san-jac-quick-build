# Use Case: Transfer Readiness & Workforce Outcomes Tracking

## Problem
San Jacinto tracks Transfer Rate, Transferability (% of SJC credits accepted at receiving universities), Completion After Transfer, Employment Rate, and Earnings after Completion as key post-graduation metrics. These are reported to THECB (CBM00T, CBM116) but are difficult to analyze at the advisor level without technical skills.

## Solution
Cortex Analyst over graduate outcome data allows advisors and institutional research staff to explore transfer and employment outcomes by program, demographic, and campus. Cortex Search over university articulation agreements and career pathway documents helps advisors answer student questions about transfer credits and job prospects.

## Demo Questions (Cortex Analyst)
- "What is the transfer rate for students completing an Associate of Arts in the last three years?"
- "Which programs have the highest employment rate within 6 months of graduation?"
- "Show me the average transferability rate by receiving university for our top 5 transfer destinations"
- "What is the licensure pass rate for Nursing graduates compared to the state average?"

## Demo Questions (Cortex Search)
- "Which of my San Jac courses will transfer to the University of Houston?"
- "What is the job placement rate for Process Technology graduates?"
- "What licensure exams are required for Dental Hygiene graduates?"

## Data Sources
- THECB outcome reports (CBM00T for transfer, CBM116 for employment)
- University articulation agreements (Cortex Search)
- Banner graduation and credential award records
- Licensure/certification exam results

## Key Fields
- `student_id`, `credential_type`, `program_code`, `transferred`, `receiving_university`, `transferability_pct`, `employed_in_field`, `earnings_estimate`, `licensure_passed`, `graduation_year`

## Expected Outcome
- Advisors can answer transfer and career questions in real time
- Institutional Research can self-serve on THECB reporting metrics
- Program-level outcome data informs curriculum and industry partnership decisions
