# San Jacinto College — Student Success Metrics Framework

Source: Institutional Effectiveness Council, Strategic Measures Recommendation (2023)

San Jacinto College tracks student success across four phases of the student experience: **Entering → Continuing → Completing → Achieving**.

---

## Entering

| Metric | Description |
|--------|-------------|
| **Admissions to Enrollment Efficiency** | % of applicants who reach the first day of enrollment |
| **Headcount (Unduplicated)** | Overall enrollment growth — longstanding strategic metric |
| **Financial Aid, Un/Met Need** | Extent to which students overcome financial barriers to begin and continue college |

---

## Continuing

| Metric | Description |
|--------|-------------|
| **Pathway Consistency** | % of students who maintain their selected program within one year (inverse of major-changers) |
| **Pathway Efficiency** | SCH attempted/completed in pathway ÷ total SCH attempted in the semester |
| **Pathway Velocity** | SCH attempted/completed in pathway ÷ total SCH required for completion |
| **Student Success (A–C)** | % of students earning A–C in courses; includes First Term GPA and Program Learning Outcomes |
| **Student Retention** | % of students who complete courses (inverse = Withdrawal Rate) |
| **Student Persistence** | Enrollment in subsequent semesters: Fall-to-Fall and Fall-to-Spring |

### Related Pathway Measures
- Full-Time/Part-Time Students
- Success Points: 1st College Level Math, 1st College Level Read/Write, 15 SCH, 30 SCH
- Complete Developmental Education
- Withdrawal Survey results / Student Self-Efficacy

---

## Completing

| Metric | Description |
|--------|-------------|
| **Degrees or Certificates Awarded** | Total number of credentials earned (included in THECB success points model) |
| **Degrees/Certificates in Critical Fields** | Awards disaggregated by THECB-defined critical instructional programs |
| **Graduation Rate (FTIC): 2-yr, 3-yr, 4-yr** | Cohort graduation rates; reported to IPEDS and THECB |
| **Average Time (Years) to Completion** | Average years to earn an associate degree (THECB definition) |
| **Semester Credit Hours to Degree** | Average SCH attempted to earn an associate degree |
| **Student Loan Default Rate** | Loan default rate per state/federal regulations |
| **Average Student Debt** | Average student loan debt at graduation |

### Related Completion Measures
- Average College Prep SCH Completed
- Average College Level SCH Completed
- Average OER-based Cost Reduction per Student

---

## Achieving (After Completion)

| Metric | Description |
|--------|-------------|
| **Transfer Rate** | % of AA/AAT/AS graduates who transfer to a university |
| **Transferability** | % of SJC courses that transferred successfully (THECB CBM00T) |
| **Completion After Transfer** | % of transfer students who earn a bachelor's degree |
| **Employment Rate (Job Placement)** | % of workforce credential completers who achieve employment in their field (THECB CBM116) |
| **Earnings after Completion** | Estimated graduate earnings post-completion |
| **Licensure/Certification Rate** | % of credential completers who pass their required licensure/certification exam |

---

## Comprehensive

| Metric | Description |
|--------|-------------|
| **Favorable Outcomes** | All credential-seeking students who persisted semester-to-semester, graduated, OR transferred |

---

## Demo Data Implications

These metrics define the key fields needed in synthetic student data:
- `pathway_id`, `program_code`, `sch_attempted`, `sch_completed`, `sch_required`
- `gpa_first_term`, `gpa_current`, `ac_success_rate`
- `retention_flag`, `persistence_fall_fall`, `persistence_fall_spring`
- `withdrawal_reason`, `loan_balance`, `pell_eligible`
- `credential_awarded`, `credential_type`, `time_to_completion_years`
- `transferred`, `employed_in_field`, `licensure_passed`
- `favorable_outcome_flag`
