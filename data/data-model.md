# San Jacinto College — Dimensional Data Model

**Version:** 0.1  
**Purpose:** Defines the star schema to support all 8 Cortex demo use cases. Used as the specification for synthetic data generation.

---

## Model Overview

The model uses a **star schema** with 5 fact tables and 8 dimension tables. The grain varies by fact table (see each table). All facts join to `dim_student` and `dim_term` at minimum.

```
dim_student ─────────────────────────────────────────┐
dim_term ─────────────────────────────────────────────┤
dim_program ─────┬── fact_enrollment                  │
dim_campus ──────┤   fact_course_attempt              ├─ dim_date
dim_stage ───────┤   fact_financial_aid               │
dim_course ──────┤   fact_student_stage_history       │
dim_credential ──┘   fact_cpd_enrollment              │
                                                      ┘
```

---

## Dimension Tables

---

### `dim_student`
**Grain:** One row per student  
**~32,000 rows** (credit students; CPD-only students handled separately in `dim_cpd_student`)

| Column | Type | Description | Generation Rules |
|--------|------|-------------|-----------------|
| `student_id` | VARCHAR PK | Unique student identifier (e.g. S000001) | Sequential, zero-padded |
| `first_name` | VARCHAR | First name | Realistic names weighted by ethnicity |
| `last_name` | VARCHAR | Last name | Realistic names weighted by ethnicity |
| `gender` | VARCHAR | Gender identity | **59% Female, 41% Male** |
| `ethnicity` | VARCHAR | Race/ethnicity | See distribution below |
| `age_at_first_enrollment` | INT | Age when first enrolled | See distribution below |
| `dob` | DATE | Date of birth | Derived from age + first enrollment term |
| `zip_code` | VARCHAR | Home zip code | **97% Texas** — weighted to SJC service area zips (see brand doc) |
| `state` | VARCHAR | State of residence | 97% TX, 3% other |
| `pell_eligible` | BOOLEAN | Receives Federal Pell Grant | **56% TRUE** |
| `first_gen_college` | BOOLEAN | First-generation college student | **~45% TRUE** (correlated with Hispanic/low-income) |
| `high_school_district` | VARCHAR | Feeder ISD | Channelview, Clear Creek, Crosby, Deer Park, etc. |
| `dual_credit` | BOOLEAN | Started as dual credit student | **~10% TRUE** |
| `hs_gpa` | DECIMAL(3,2) | High school GPA | Normal distribution, mean 2.8, SD 0.5, range 1.5–4.0 |
| `tsi_math_exempt` | BOOLEAN | TSI math exempt/satisfied | **~65% TRUE** |
| `tsi_reading_exempt` | BOOLEAN | TSI reading/writing exempt | **~70% TRUE** |
| `meningitis_submitted` | BOOLEAN | Meningitis doc on file | **~85% TRUE** of admitted+ students |
| `nso_complete` | BOOLEAN | New Student Orientation complete | **~80% TRUE** of admitted+ students |
| `created_date` | DATE | Record creation date | Varies by term cohort |

**Ethnicity Distribution:**
| Value | % |
|-------|---|
| Hispanic or Latino | 63.3% |
| White | 15.2% |
| Black or African American | 8.5% |
| Asian | 5.0% |
| Two or More Races | 1.9% |
| Unknown / Not Reported | 5.1% |
| American Indian / Alaska Native | 0.6% |
| Native Hawaiian / Pacific Islander | 0.4% |

**Age Distribution (at first enrollment):**
| Range | % |
|-------|---|
| Under 18 (dual credit) | 5% |
| 18–21 (traditional) | 45% |
| 22–25 | 20% |
| 26–35 | 18% |
| 36–50 | 10% |
| 51+ | 2% |

---

### `dim_term`
**Grain:** One row per academic term

| Column | Type | Description | Generation Rules |
|--------|------|-------------|-----------------|
| `term_id` | VARCHAR PK | e.g. `2024FA`, `2025SP`, `2025SU` | |
| `term_name` | VARCHAR | e.g. "Fall 2024" | |
| `term_season` | VARCHAR | Fall / Spring / Summer | |
| `academic_year` | VARCHAR | e.g. "2024–25" | |
| `start_date` | DATE | First day of term | |
| `end_date` | DATE | Last day of term | |
| `census_date` | DATE | Official enrollment count date | ~12th class day |
| `is_current_term` | BOOLEAN | Flag for current term | Only one TRUE at a time |

**Generate:** 6 terms minimum (3 academic years: 2022–23, 2023–24, 2024–25) to support trend queries.

---

### `dim_program`
**Grain:** One row per program (credit credential)  
**~200+ rows**

| Column | Type | Description | Generation Rules |
|--------|------|-------------|-----------------|
| `program_id` | VARCHAR PK | e.g. `BUS-AAS-001` | |
| `program_name` | VARCHAR | Full program name | From programs-catalog.md |
| `credential_type` | VARCHAR | AAS / AA / AS / Certificate of Technology / Level 2 Cert / Occupational Cert / ATC / BAT / BAS / AAT | |
| `area_of_study` | VARCHAR | Top-level academic area | See values below |
| `is_transfer` | BOOLEAN | Academic transfer pathway (AA/AS/AAT) | |
| `is_workforce` | BOOLEAN | Workforce/technical credential | |
| `is_critical_field` | BOOLEAN | THECB critical field designation | **~30% TRUE** (Health Sciences, STEM, trades) |
| `sch_required` | INT | Total SCH required for completion | AA/AS: 60; AAS: 60–72; Certs: 15–45 |
| `typical_completion_semesters` | INT | Expected semesters to complete full-time | AA/AS: 4; AAS: 4–6; Certs: 2–4 |
| `licensure_required` | BOOLEAN | Requires licensure/certification exam | ~15% TRUE (Nursing, Dental, EMS, etc.) |
| `campus_primary` | VARCHAR | Primary campus where program is offered | Central / North / South / Gen Park / Maritime |

**Area of Study Values:**
- Arts, Humanities, Communications & Design
- Business
- Construction, Industry, Manufacturing & Transportation
- Education
- Health Sciences
- Information Technology
- Science & Mathematics
- Social & Behavioral Sciences
- Public Safety & Criminal Justice

---

### `dim_course`
**Grain:** One row per unique course (prefix + number)  
**~800–1,000 rows**

| Column | Type | Description | Generation Rules |
|--------|------|-------------|-----------------|
| `course_id` | VARCHAR PK | e.g. `MATH-1314` | |
| `course_prefix` | VARCHAR | e.g. `MATH`, `ENGL`, `BIOL` | |
| `course_number` | VARCHAR | e.g. `1314` | |
| `course_title` | VARCHAR | Full title | e.g. "College Algebra" |
| `sch_value` | INT | Semester credit hours | Mostly 3; some 1–4 |
| `course_level` | VARCHAR | College-level / Developmental | **~15% Developmental** |
| `delivery_mode` | VARCHAR | Face-to-face / Online / Hybrid | See distribution below |
| `area_of_study` | VARCHAR | Matches dim_program area | |
| `is_gateway` | BOOLEAN | First college-level math or reading/writing | ~2% TRUE — important for success points |

**Delivery Mode Distribution (per section):**
| Mode | % |
|------|---|
| Face-to-face | 38% |
| Online | 30% |
| Hybrid | 32% |

---

### `dim_campus`
**Grain:** One row per campus  
**5 rows**

| `campus_id` | `campus_name` |
|-------------|---------------|
| CEN | Central Campus |
| NOR | North Campus |
| SOU | South Campus |
| GEN | Generation Park Campus |
| MAR | Maritime Campus |

---

### `dim_stage`
**Grain:** One row per TargetX student stage  
**11 rows**

| `stage_id` | `stage_name` | `flow_type` | `is_active_student` | `sort_order` |
|------------|-------------|-------------|---------------------|-------------|
| 1 | Prospective | Record-Triggered | FALSE | 1 |
| 2 | Applicant | Record-Triggered | FALSE | 2 |
| 3 | Not Interested | Record-Triggered | FALSE | 99 |
| 4 | Admitted | Record-Triggered | FALSE | 3 |
| 5 | Eligible to Register – New | Record-Triggered | FALSE | 4 |
| 6 | Register Pending | Record-Triggered | FALSE | 5 |
| 7 | Eligible to Register – Continuing | Date-Based | FALSE | 6 |
| 8 | Enrolled | Record-Triggered | TRUE | 7 |
| 9 | Graduate / Alumni | Record-Triggered | FALSE | 8 |
| 10 | Stop-Out | Date-Based | FALSE | 9 |
| 11 | Recruit Backs | Date-Based | FALSE | 10 |

---

### `dim_credential`
**Grain:** One row per awarded credential type  
**Reference table**

| Column | Type | Description |
|--------|------|-------------|
| `credential_id` | VARCHAR PK | |
| `credential_type` | VARCHAR | AAS, AA, AS, AAT, BAT, BAS, Cert of Tech, Level 2 Cert, Occupational Cert, ATC |
| `credential_level` | VARCHAR | Bachelor / Associate / Certificate |
| `transfer_eligible` | BOOLEAN | TRUE for AA, AS, AAT |

---

## Fact Tables

---

### `fact_enrollment`
**Grain:** One row per student per term  
**~85,000 rows** (32,000 students × ~2.7 active terms on average)

| Column | Type | Description | Generation Rules |
|--------|------|-------------|-----------------|
| `enrollment_id` | BIGINT PK | Surrogate key | |
| `student_id` | VARCHAR FK | → dim_student | |
| `term_id` | VARCHAR FK | → dim_term | |
| `program_id` | VARCHAR FK | → dim_program (declared major) | |
| `campus_id` | VARCHAR FK | → dim_campus | |
| `stage_id` | INT FK | → dim_stage (stage at census date) | |
| `enrollment_type` | VARCHAR | First-Time-in-College / Transfer / Continuing / Re-admit | **FTIC: 25%, Transfer: 10%, Continuing: 60%, Re-admit: 5%** |
| `total_sch_attempted` | INT | Total SCH registered | Full-time (12+): **33.8%**; Part-time (<12): **66.2%** |
| `total_sch_completed` | INT | SCH successfully completed (grade ≥ D or pass) | |
| `sch_on_pathway` | INT | SCH that count toward declared program | ~85% of completed SCH on average |
| `is_online_only` | BOOLEAN | All courses online | **30% TRUE** |
| `has_some_online` | BOOLEAN | Mix of online and face-to-face | **32% TRUE** among non-online-only |
| `payment_status` | VARCHAR | Paid / Payment Plan / Aid Authorized / Unpaid | Unpaid → Register Pending stage |
| `mf_hold_active` | BOOLEAN | Active MF hold blocking registration | Admitted stage only |
| `is_first_term` | BOOLEAN | First ever term at SJC | |
| `withdrew_term` | BOOLEAN | Withdrew from all courses mid-term | **~8% TRUE** |
| `financial_aid_term` | BOOLEAN | Received any financial aid this term | **~60% TRUE** |

**SCH Distribution:**
| Range | Label | % of enrollments |
|-------|-------|-----------------|
| 1–5 | Very Part-Time | 15% |
| 6–8 | Part-Time | 28% |
| 9–11 | Near Full-Time | 24% |
| 12–14 | Full-Time | 26% |
| 15+ | Overload | 7% |

**Stage at Census Date Distribution (current term):**
| Stage | % |
|-------|---|
| Enrolled | 62% |
| Register Pending | 4% |
| Eligible to Register – Continuing | 8% |
| Eligible to Register – New | 4% |
| Admitted | 3% |
| Graduate / Alumni | 8% |
| Stop-Out | 6% |
| Recruit Backs | 2% |
| Prospective / Applicant | 2% |
| Not Interested | 1% |

---

### `fact_course_attempt`
**Grain:** One row per student per course section per term  
**~250,000 rows** (average ~3 courses per enrolled student per term)

| Column | Type | Description | Generation Rules |
|--------|------|-------------|-----------------|
| `attempt_id` | BIGINT PK | Surrogate key | |
| `student_id` | VARCHAR FK | → dim_student | |
| `term_id` | VARCHAR FK | → dim_term | |
| `course_id` | VARCHAR FK | → dim_course | |
| `campus_id` | VARCHAR FK | → dim_campus | |
| `section_id` | VARCHAR | Course section identifier | |
| `delivery_mode` | VARCHAR | Face-to-face / Online / Hybrid | |
| `instructor_id` | VARCHAR | Anonymized instructor ID | |
| `grade` | VARCHAR | A / B / C / D / F / W / I | See distribution below |
| `grade_points` | DECIMAL(3,1) | 4.0 scale | A=4, B=3, C=2, D=1, F=0, W/I=null |
| `ac_success` | BOOLEAN | Grade of A, B, or C | **~72% TRUE** overall |
| `withdrew` | BOOLEAN | W grade (student-initiated withdrawal) | **~12% TRUE** |
| `sch_earned` | INT | SCH earned (0 if W/F) | |
| `is_developmental` | BOOLEAN | Dev ed course | **~15% of all attempts** |
| `attendance_pct` | DECIMAL(5,2) | % of class sessions attended | Normal dist; mean 82%, SD 15% |
| `midterm_grade` | VARCHAR | A / B / C / D / F | Leading indicator for early alert |

**Grade Distribution (non-withdrawn):**
| Grade | % of non-W attempts |
|-------|-------------------|
| A | 35% |
| B | 22% |
| C | 15% |
| D | 8% |
| F | 20% |

**Restrictions:**
- Withdrawal rate higher for: developmental courses (**~22% W**), first-term students (**+5%**), part-time working students
- A–C success rate higher for: full-time students, continuing students, students with complete financial aid
- A–C success rate lower for: developmental courses (**~55%**), students with attendance_pct < 70%

---

### `fact_financial_aid`
**Grain:** One row per student per term per aid type  
**~60,000 rows**

| Column | Type | Description | Generation Rules |
|--------|------|-------------|-----------------|
| `aid_id` | BIGINT PK | Surrogate key | |
| `student_id` | VARCHAR FK | → dim_student | |
| `term_id` | VARCHAR FK | → dim_term | |
| `aid_type` | VARCHAR | Pell Grant / TPEG / Workforce Solutions / Institutional / Loan / Work-Study | |
| `aid_amount_awarded` | DECIMAL(8,2) | Aid awarded for the term | |
| `aid_amount_disbursed` | DECIMAL(8,2) | Aid actually disbursed | |
| `unmet_need` | DECIMAL(8,2) | Cost of attendance minus all aid | |
| `disbursement_status` | VARCHAR | Pending / Disbursed / Cancelled | |
| `satisfactory_academic_progress` | BOOLEAN | SAP met | **~85% TRUE** |
| `enrollment_intensity_required` | INT | Minimum SCH for aid | Pell = 6 SCH minimum for half |
| `cumulative_loan_balance` | DECIMAL(10,2) | Total loan debt to date | Only for loan-type records |

**Aid Type Distribution (among aid recipients):**
| Type | % of aided students |
|------|-------------------|
| Pell Grant | 56% of all students; avg award ~$3,200/term |
| TPEG | 15% of Pell-eligible students |
| Institutional Grant | 10% |
| Workforce Solutions | 8% of CPD/workforce program students |
| Student Loan | 12% |
| Work-Study | 3% |

**Unmet Need Distribution:**
| Range | % |
|-------|---|
| $0 (fully covered) | 20% |
| $1–$500 | 25% |
| $501–$1,500 | 30% |
| $1,501–$3,000 | 15% |
| $3,001+ | 10% |

---

### `fact_student_stage_history`
**Grain:** One row per student per stage transition  
**~90,000 rows** (avg ~2.8 stage changes per student lifetime)

| Column | Type | Description | Generation Rules |
|--------|------|-------------|-----------------|
| `history_id` | BIGINT PK | Surrogate key | |
| `student_id` | VARCHAR FK | → dim_student | |
| `stage_id` | INT FK | → dim_stage | |
| `stage_start_date` | DATE | Date entered this stage | |
| `stage_end_date` | DATE | Date exited this stage (NULL if current) | |
| `days_in_stage` | INT | Computed duration | |
| `previous_stage_id` | INT | Stage they came from | |
| `trigger_type` | VARCHAR | Record-Triggered / Date-Based | |
| `term_id` | VARCHAR FK | Term associated with transition | |

**Stage Transition Rules:**
- Prospective → Applicant: median 14 days after inquiry
- Applicant → Admitted: median 21 days after application accepted
- Admitted → Eligible to Register – New: MF hold cleared, median 7 days
- Eligible to Register – New → Register Pending: median 5 days
- Register Pending → Enrolled: payment confirmed, median 3 days
- Enrolled → Eligible to Register – Continuing: triggered 4 weeks before term end
- Eligible to Register – Continuing → Stop-Out: after 3 terms without re-enrollment
- Enrolled → Graduate/Alumni: upon credential award
- **~8% of Applicants → Not Interested** (Banner = "Student Withdrawal")
- **~15% of Eligible to Register – New → Recruit Backs** (stalled > 6 months)

---

### `fact_cpd_enrollment`
**Grain:** One row per CPD student per course enrollment  
**~20,000 rows**

| Column | Type | Description | Generation Rules |
|--------|------|-------------|-----------------|
| `cpd_enrollment_id` | BIGINT PK | Surrogate key | |
| `cpd_student_id` | VARCHAR FK | → dim_cpd_student (separate dimension) | |
| `term_id` | VARCHAR FK | → dim_term | |
| `course_id` | VARCHAR | CPD course code | |
| `course_name` | VARCHAR | CPD course name | |
| `cpd_center` | VARCHAR | EDGE / BIT / Corporate / Community & Health | See distribution below |
| `campus_id` | VARCHAR FK | → dim_campus | |
| `delivery_mode` | VARCHAR | In-Person / Online / Hybrid | |
| `enrollment_date` | DATE | Registration date | |
| `completion_status` | VARCHAR | Completed / In Progress / Dropped / No-Show | **Completed: 78%, Dropped: 12%, No-Show: 10%** |
| `seat_capacity` | INT | Max seats in course | |
| `grant_funded` | BOOLEAN | TPEG or Workforce Solutions grant | **~25% TRUE** |
| `employer_sponsored` | BOOLEAN | Paid by employer / corporate contract | **~20% TRUE** |
| `linked_to_credit` | BOOLEAN | "Linked" course — credit applicable | **~10% TRUE** |

**CPD Center Distribution:**
| Center | % |
|--------|---|
| EDGE (Aerospace/Aviation/Mfg) | 18% |
| BIT (IT/AI/Business/Logistics) | 25% |
| Corporate (Apprenticeships/Grants) | 22% |
| Community & Health | 35% |

---

## Key Metric Definitions (for validation)

Use these to validate generated data produces correct aggregate values:

| Metric | Target Value | Calculation |
|--------|-------------|-------------|
| Total active credit students | ~31,812 | COUNT(DISTINCT student_id) in current term enrolled |
| Full-time rate | 33.8% | % with total_sch_attempted ≥ 12 |
| Online-only rate | 30% | % with is_online_only = TRUE |
| Pell eligibility rate | 56% | % of dim_student with pell_eligible = TRUE |
| Hispanic enrollment | 63.3% | % of dim_student with ethnicity = 'Hispanic or Latino' |
| Female enrollment | 59% | % of dim_student with gender = 'Female' |
| A–C course success rate | ~72% | % of fact_course_attempt where ac_success = TRUE (excl. W) |
| Withdrawal rate | ~12% | % of fact_course_attempt where withdrew = TRUE |
| Fall-to-Fall persistence | ~55% | % of Fall enrolled students also enrolled next Fall |
| Fall-to-Spring persistence | ~68% | % of Fall enrolled students also enrolled same Spring |
| Graduation rate (3-yr FTIC) | ~18% | % of FTIC cohort awarding credential within 3 years |
| Transfer rate | ~22% | % of AA/AS/AAT completers who transfer |
| Stop-Out rate | ~6% | % of student population in Stop-Out stage |
| Recruit Backs rate | ~2% | % of student population in Recruit Backs stage |

---

## Referential Integrity & Constraint Notes

- Every `fact_enrollment` row must have a valid `student_id`, `term_id`, `program_id`, `campus_id`
- A student in stage **Enrolled** must have `payment_status` IN ('Paid', 'Payment Plan', 'Aid Authorized')
- A student in stage **Register Pending** must have `payment_status = 'Unpaid'` and a future/current academic profile
- A student in stage **Admitted** must have `mf_hold_active = TRUE`
- A student in stage **Eligible to Register – New** must have all three: `tsi_*_exempt = TRUE`, `meningitis_submitted = TRUE`, `nso_complete = TRUE`, and `mf_hold_active = FALSE`
- `sch_on_pathway` must be ≤ `total_sch_completed`
- `aid_amount_disbursed` must be ≤ `aid_amount_awarded`
- Students with `pell_eligible = FALSE` should not have Pell Grant records in `fact_financial_aid`
- `dual_credit = TRUE` students should have `age_at_first_enrollment < 18`
- Developmental course attempts (`is_developmental = TRUE`) should only appear in first 1–2 terms

---

## Correlated Distributions (important for realism)

These correlations should be applied during generation — not all fields are independent:

| If... | Then... |
|-------|---------|
| `pell_eligible = TRUE` | Higher probability of `unmet_need > 0`, `first_gen = TRUE`, `part-time` enrollment |
| `ethnicity = Hispanic` | Higher probability of `pell_eligible = TRUE` (~65%), `first_gen = TRUE` (~50%) |
| `is_online_only = TRUE` | Higher probability of part-time, age > 25, working student |
| `enrollment_type = FTIC` | Higher probability of dev ed courses, lower A–C success rate in first term |
| `attendance_pct < 70%` | Higher probability of W grade or F grade |
| `total_sch_attempted ≥ 12` | Higher A–C success rate, higher persistence rate |
| `financial_aid_term = TRUE` | Lower withdrawal rate, higher persistence |
| `is_developmental = TRUE` (course) | Lower A–C success rate (~55%), higher W rate (~22%) |
| `program.licensure_required = TRUE` | Higher course success required; lower graduation rate if failed |
| `stage = Stop-Out` | `terms_since_last_enrollment` between 3–8 |
| `stage = Recruit Backs` | Time in Eligible to Register – New > 180 days, no registration ever |
