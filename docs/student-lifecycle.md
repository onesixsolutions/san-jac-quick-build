# San Jacinto College — Student Lifecycle

Source: TargetX Student Stages (San Jacinto College CRM system)

San Jacinto College tracks students through a defined set of stages in TargetX (Salesforce-based CRM), integrated with Banner (SIS). Stage transitions are triggered either by record events or date-based rules.

---

## Student Stages

| Stage | Definition | Trigger Type |
|-------|-----------|--------------|
| **Prospective** | Filled out an inquiry or event form; no prior contact or application record exists | Record-Triggered |
| **Applicant** | Completed ApplyTexas application, processed and accepted in Banner; no academic profile for last 3 semesters or future profile | Record-Triggered |
| **Not Interested** | Submitted an application but withdrew interest; Banner application decision = "Student Withdrawal" | Record-Triggered |
| **Admitted** | Met all checklist items (TSI, meningitis docs, NSO) AND has an **active** MF hold with end date 12/31/2099 | Record-Triggered |
| **Eligible to Register – New** | Met all checklist items (TSI, meningitis docs, NSO) AND has an **inactive** MF hold with end date today or past | Record-Triggered |
| **Register Pending** | Has current or future academic profile (registered for classes) but **no payment** for the term | Record-Triggered |
| **Eligible to Register – Continuing** | Previously enrolled but not enrolled in a current or future term; can remain in this stage up to 3 terms | Date-Based |
| **Enrolled** | Registered for classes AND payment complete (paid in full, payment plan, or authorized financial aid) | Record-Triggered |
| **Graduate / Alumni** | Awarded a credential | Record-Triggered |
| **Stop-Out** | Has course history but has not enrolled in the last 3 terms | Date-Based |
| **Recruit Backs** | Was in "Eligible to Register – New" but never progressed past that stage | Date-Based |

---

## Admission Checklist (Required for Admitted / Eligible to Register)

1. TSI proof or exemption in all areas
2. Meningitis documentation (if applicable)
3. Completed New Student Orientation (NSO, if applicable)

**MF Hold logic:**
- **Active** MF hold (end date 12/31/2099) → **Admitted** (not yet cleared to register)
- **Inactive** MF hold (end date today or past) → **Eligible to Register – New**

---

## Date-Based Flow Timing

Date-based stage transitions occur:
- **4 weeks** before the end of any Fall or Spring term
- **5 weeks** before the end of any Summer term

Stages using date-based flow: Eligible to Register – Continuing, Stop-Out, Recruit Backs

---

## Lifecycle Flow Diagram

```
Prospective
    ↓
Applicant ──→ Not Interested
    ↓
Admitted
    ↓
Eligible to Register – New ──→ Recruit Backs (if stalled)
    ↓
Register Pending
    ↓
Enrolled
    ↓
Graduate / Alumni
    
Re-enrollment path:
Eligible to Register – Continuing (up to 3 terms out)
    ↓ (after 3 terms)
Stop-Out
```

---

## Demo Data Implications

Key fields for synthetic student data aligned to this lifecycle:

| Field | Values |
|-------|--------|
| `student_stage` | Prospective, Applicant, Not Interested, Admitted, Eligible to Register-New, Register Pending, Eligible to Register-Continuing, Enrolled, Graduate/Alumni, Stop-Out, Recruit Backs |
| `tsi_complete` | Boolean |
| `meningitis_doc_submitted` | Boolean |
| `nso_complete` | Boolean |
| `mf_hold_active` | Boolean |
| `mf_hold_end_date` | Date |
| `has_future_academic_profile` | Boolean |
| `payment_status` | None, Paid, Payment Plan, Aid Authorized |
| `terms_since_last_enrollment` | Integer (drives Continuing → Stop-Out) |
| `credential_awarded` | Boolean |
| `banner_application_decision` | Accepted, Student Withdrawal, etc. |

---

## System Integration Notes

- **TargetX** (Salesforce CRM) manages stage tracking and automated outreach flows
- **Banner** (SIS) is the system of record for application decisions, academic profiles, holds, and registration
- **ApplyTexas** is the application portal feeding into Banner
