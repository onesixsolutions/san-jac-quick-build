# Use Case: Pathway Velocity & Completion Risk Scoring

## Problem
San Jacinto tracks Pathway Consistency, Pathway Efficiency, and Pathway Velocity as core strategic metrics — but computing and acting on these metrics at scale requires SQL expertise that most advisors don't have. Students who are off-pace for completion often aren't flagged until it's too late.

## Solution
Cortex Analyst over enrollment and SCH data lets advisors ask natural language questions about pathway progress. A Snowpark ML model scores completion risk based on pathway velocity (SCH on-path ÷ SCH required) and flags students for proactive intervention. Results surface in the Streamlit advisor app.

## Demo Questions (Cortex Analyst)
- "Which students in the Logistics AAS program are completing less than 60% of their required pathway credits each semester?"
- "What is the average pathway velocity for students in the Process Technology program compared to last year?"
- "Show me students who changed their major more than once in the past 12 months"

## Key Metrics
- **Pathway Efficiency** = SCH on-path attempted/completed ÷ total SCH attempted
- **Pathway Velocity** = SCH on-path ÷ total SCH required for completion
- **Pathway Consistency** = % of students maintaining their declared program within one year

## Data Sources
- Banner enrollment records (SCH attempted, SCH completed, program code)
- Program requirements table (SCH required per credential)
- Historical pathway change records

## Key Fields
- `student_id`, `program_code`, `sch_attempted`, `sch_completed_on_path`, `sch_required_total`, `major_change_count`, `pathway_velocity_score`

## Expected Outcome
- Early identification of students at risk of not completing on time
- Advisor intervention prioritized by velocity score
- Reduction in average time-to-completion and student debt accumulation
