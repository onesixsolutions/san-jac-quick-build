# Use Case: CPD / Workforce Program Demand Analysis

## Problem
San Jacinto's Continuing & Professional Development (CPD) division serves thousands of non-credit learners across four specialized centers (EDGE, BIT, Corporate, Community & Health). Program managers need to understand enrollment trends, seat utilization, and regional workforce demand — but this data is siloed and hard to query without SQL.

## Solution
Cortex Analyst over CPD enrollment and completion data lets program managers and workforce development staff ask natural language questions about program performance. Cortex Search over course descriptions and industry partnership docs helps identify gaps between program offerings and regional employer needs (petrochemical, maritime, aerospace, biomanufacturing).

## Demo Questions (Cortex Analyst)
- "Which CPD programs have seen the biggest enrollment growth in the last two years?"
- "What is the seat utilization rate for Maritime courses across all campuses?"
- "Show me completion rates for Biomanufacturing vs. Aerospace programs at the EDGE Center"
- "How many students have used TPEG grants for workforce training programs?"

## Demo Questions (Cortex Search)
- "What CPD programs are available for someone working in the petrochemical industry?"
- "What are the prerequisites for the FAA Part 107 Drone Pilot certification course?"

## Data Sources
- CPD enrollment and completion records
- Course catalog (Cortex Search)
- TPEG and Workforce Solutions grant utilization data
- Employer partnership and industry demand data

## Key Fields
- `course_id`, `center_name` (EDGE/BIT/Corporate/Community & Health), `enrollment_count`, `completion_count`, `seat_capacity`, `grant_funded`, `employer_partner`

## Expected Outcome
- Program managers can self-serve on enrollment analytics without SQL
- Proactive identification of high-demand, under-capacity programs
- Better alignment between CPD offerings and Houston-area workforce needs
