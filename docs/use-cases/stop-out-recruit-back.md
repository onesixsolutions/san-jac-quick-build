# Use Case: Stop-Out & Recruit-Back Identification

## Problem
Students who go "Stop-Out" (no enrollment for 3+ terms) or get stuck in "Recruit Backs" (admitted but never registered) represent lost opportunity — both for the student and for San Jacinto. With 31,800+ students across all stages, manual outreach to re-engage these populations is inconsistent and slow.

## Solution
Cortex Analyst over structured TargetX/Banner data surfaces at-risk students by stage. Cortex Search over prior advising notes and program history enables advisors to understand why a student stopped out and what programs might re-engage them. The Streamlit app provides a re-engagement dashboard with prioritized outreach lists.

## Demo Questions (Cortex Analyst)
- "How many students moved to Stop-Out status in the last two terms?"
- "Which students in the Recruit Backs stage have been stalled for more than 6 months?"
- "Show me Stop-Out students who previously enrolled in Health Sciences programs"

## Data Sources
- TargetX student stage history table
- Banner enrollment and academic profile records
- Program interest / prior advising notes (Cortex Search)

## Key Fields
- `student_stage`, `terms_since_last_enrollment`, `prior_program_code`, `mf_hold_active`, `stage_change_date`

## Expected Outcome
- Prioritized re-engagement lists for advising and recruiting staff
- Targeted outreach by program area and time-out-of-enrollment
- Improved Favorable Outcomes metric (persistence + graduation + transfer)
