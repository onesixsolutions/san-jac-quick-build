# Use Case: Financial Aid Gap & Pell Eligibility Monitoring

## Problem
56% of San Jacinto students are Pell-eligible (low-income), yet financial barriers are a leading cause of enrollment drop-off and stop-out. The Admissions to Enrollment Efficiency metric and Financial Aid Un/Met Need metric both depend on identifying students whose financial situations are creating friction — but this requires cross-referencing aid data, enrollment status, and payment holds in Banner.

## Solution
Cortex Analyst over Banner financial aid and enrollment data allows Financial Aid staff and advisors to ask natural language questions about aid gaps, payment holds, and at-risk students. Cortex Search over financial aid policy documents allows students and advisors to quickly find answers to aid questions without calling the financial aid office.

## Demo Questions (Cortex Analyst)
- "How many students in 'Register Pending' status have no financial aid package for this academic period?"
- "What percentage of Pell-eligible applicants did not complete enrollment this academic period?"
- "Show me students with unmet financial need who are in their first academic period"

## Demo Questions (Cortex Search)
- "What is the process for a financial aid appeal at San Jacinto?"
- "How do I apply for the Texas Public Education Grant for CPD courses?"
- "What happens to my financial aid if I drop below 6 credit hours?"

## Data Sources
- Banner financial aid records (aid type, award amount, disbursement status)
- Enrollment and payment status (Register Pending vs. Enrolled)
- FAFSA/TPEG/Workforce Solutions grant data
- Financial aid policy documents (Cortex Search)

## Key Fields
- `student_id`, `pell_eligible`, `aid_awarded`, `aid_disbursed`, `unmet_need`, `payment_status`, `student_stage`, `term_enrolled`

## Expected Outcome
- Faster identification of students at risk of dropping due to financial barriers
- Proactive outreach before payment deadlines
- Improved Admissions-to-Enrollment Efficiency and Favorable Outcomes metrics
