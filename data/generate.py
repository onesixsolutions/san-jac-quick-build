"""
San Jacinto College — Synthetic Data Generator
===============================================
Generates all 13 tables (8 dimensions + 5 facts) per data/data-model.md.

Output: CSV files in data/output/

Usage:
    pip install -r data/requirements.txt
    python data/generate.py

Seed: 42 (fully reproducible)
Scale: ~32,000 students | ~85K enrollments | ~250K course attempts
"""

import io
import os
import sys
import random
from datetime import date, timedelta
from pathlib import Path

# Ensure UTF-8 output on Windows
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
from faker import Faker

# ── Config ────────────────────────────────────────────────────────────────────

SEED         = 42
N_STUDENTS   = 32_000
N_CPD        = 4_000
OUTPUT_DIR   = Path(__file__).parent / "output"
CURRENT_TERM = "2026SP"

random.seed(SEED)
np.random.seed(SEED)
fake = Faker("en_US")
Faker.seed(SEED)
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Term definitions ──────────────────────────────────────────────────────────

TERM_ORDER = [
    "2022FA","2023SP","2023SU","2023FA","2024SP","2024SU",
    "2024FA","2025SP","2025SU","2025FA","2026SP",
]
TERM_IDX = {t: i for i, t in enumerate(TERM_ORDER)}

# (season, academic_year, start, end, census)
TERM_META = {
    "2022FA": ("Fall",   "2022-23", date(2022, 8,22), date(2022,12,16), date(2022, 9, 2)),
    "2023SP": ("Spring", "2022-23", date(2023, 1,17), date(2023, 5,12), date(2023, 1,30)),
    "2023SU": ("Summer", "2022-23", date(2023, 6, 5), date(2023, 8, 4), date(2023, 6,16)),
    "2023FA": ("Fall",   "2023-24", date(2023, 8,21), date(2023,12,15), date(2023, 9, 1)),
    "2024SP": ("Spring", "2023-24", date(2024, 1,16), date(2024, 5,10), date(2024, 1,29)),
    "2024SU": ("Summer", "2023-24", date(2024, 6, 3), date(2024, 8, 2), date(2024, 6,14)),
    "2024FA": ("Fall",   "2024-25", date(2024, 8,19), date(2024,12,13), date(2024, 8,30)),
    "2025SP": ("Spring", "2024-25", date(2025, 1,14), date(2025, 5, 9), date(2025, 1,27)),
    "2025SU": ("Summer", "2024-25", date(2025, 6, 2), date(2025, 8, 1), date(2025, 6,13)),
    "2025FA": ("Fall",   "2025-26", date(2025, 8,18), date(2025,12,12), date(2025, 8,29)),
    "2026SP": ("Spring", "2025-26", date(2026, 1,13), date(2026, 5, 8), date(2026, 1,26)),
}

# ── Geography ─────────────────────────────────────────────────────────────────

SJC_ZIPS = [
    "77505","77502","77503","77506","77507","77504","77547","77571","77536",
    "77029","77015","77013","77049","77034","77089","77598","77062","77058",
    "77586","77059","77530","77028","77044","77587","77078",
]
TX_OTHER_ZIPS = ["77001","77002","77003","77004","77005","77056","77057","77401","77701","78201"]
OOS_ZIPS      = ["90001","30301","60601","10001","85001","98101"]

FEEDER_ISDS = [
    "Channelview ISD","Clear Creek ISD","Crosby ISD","Deer Park ISD",
    "Galena Park ISD","Goose Creek CISD","Houston ISD","La Porte ISD",
    "Pasadena ISD","Sheldon ISD","South Houston ISD",
]

# ── Name pools (ethnicity-weighted) ──────────────────────────────────────────

HISP_FIRST_F = ["Maria","Ana","Sofia","Isabella","Valentina","Camila","Gabriela",
                "Andrea","Daniela","Laura","Rosa","Elena","Patricia","Monica","Carmen",
                "Lucia","Alejandra","Mariana","Adriana","Fernanda"]
HISP_FIRST_M = ["Carlos","Miguel","Jose","Juan","Luis","Diego","Alejandro","Ricardo",
                "Roberto","Eduardo","Fernando","Marco","Angel","Javier","David",
                "Manuel","Jorge","Rafael","Antonio","Francisco"]
HISP_LAST    = ["Garcia","Martinez","Rodriguez","Lopez","Hernandez","Gonzalez","Perez",
                "Ramirez","Torres","Flores","Rivera","Morales","Ortiz","Reyes","Cruz",
                "Sanchez","Rojas","Diaz","Mendoza","Gutierrez"]

# ── Helpers ───────────────────────────────────────────────────────────────────

def wchoice(options, weights, k=1):
    result = random.choices(options, weights=weights, k=k)
    return result[0] if k == 1 else result

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

def rand_date_between(d1, d2):
    delta = (d2 - d1).days
    return d1 + timedelta(days=random.randint(0, max(delta, 0)))

def save(df, name):
    path = OUTPUT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    print(f"  ✓  {name}.csv  —  {len(df):,} rows")
    return df

# ─────────────────────────────────────────────────────────────────────────────
# DIMENSION GENERATORS
# ─────────────────────────────────────────────────────────────────────────────

def gen_dim_campus():
    rows = [
        ("CEN", "Central Campus",         "8060 Spencer Hwy",   "Pasadena", "TX"),
        ("NOR", "North Campus",            "5800 Uvalde Rd",     "Houston",  "TX"),
        ("SOU", "South Campus",            "13735 Beamer Rd",    "Houston",  "TX"),
        ("GEN", "Generation Park Campus",  "12603 Equal Justice","Houston",  "TX"),
        ("MAR", "Maritime Campus",         "5800 Uvalde Rd",     "Houston",  "TX"),
    ]
    df = pd.DataFrame(rows, columns=["campus_id","campus_name","street","city","state"])
    return save(df, "dim_campus")


def gen_dim_stage():
    rows = [
        (1,  "Prospective",                     "Record-Triggered", False, 1),
        (2,  "Applicant",                        "Record-Triggered", False, 2),
        (3,  "Not Interested",                   "Record-Triggered", False, 99),
        (4,  "Admitted",                         "Record-Triggered", False, 3),
        (5,  "Eligible to Register - New",       "Record-Triggered", False, 4),
        (6,  "Register Pending",                 "Record-Triggered", False, 5),
        (7,  "Eligible to Register - Continuing","Date-Based",       False, 6),
        (8,  "Enrolled",                         "Record-Triggered", True,  7),
        (9,  "Graduate / Alumni",                "Record-Triggered", False, 8),
        (10, "Stop-Out",                         "Date-Based",       False, 9),
        (11, "Recruit Backs",                    "Date-Based",       False, 10),
    ]
    df = pd.DataFrame(rows, columns=[
        "stage_id","stage_name","flow_type","is_active_student","sort_order"
    ])
    return save(df, "dim_stage")


def gen_dim_credential():
    rows = [
        ("CRED-AA",  "Associate of Arts",              "Associate",   True),
        ("CRED-AS",  "Associate of Science",            "Associate",   True),
        ("CRED-AAT", "Associate of Arts in Teaching",   "Associate",   True),
        ("CRED-AAS", "Associate of Applied Science",    "Associate",   False),
        ("CRED-BAT", "Bachelor of Applied Technology",  "Bachelor",    False),
        ("CRED-BAS", "Bachelor of Applied Science",     "Bachelor",    False),
        ("CRED-COT", "Certificate of Technology",       "Certificate", False),
        ("CRED-L2C", "Level 2 Certificate",             "Certificate", False),
        ("CRED-OCC", "Occupational Certificate",        "Certificate", False),
        ("CRED-ATC", "Advanced Technical Certificate",  "Certificate", False),
        ("CRED-ESC", "Enhanced Skills Certificate",     "Certificate", False),
    ]
    df = pd.DataFrame(rows, columns=[
        "credential_id","credential_type","credential_level","transfer_eligible"
    ])
    return save(df, "dim_credential")


def gen_dim_term():
    rows = []
    for tid in TERM_ORDER:
        season, ay, start, end, census = TERM_META[tid]
        rows.append({
            "term_id":        tid,
            "term_name":      f"{season} {tid[:4]}",
            "term_season":    season,
            "academic_year":  ay,
            "start_date":     start,
            "end_date":       end,
            "census_date":    census,
            "is_current_term": tid == CURRENT_TERM,
        })
    return save(pd.DataFrame(rows), "dim_term")


def gen_dim_program():
    # (area, name, cred_id, is_transfer, is_workforce, is_critical, sch_req, typ_sem, lic_req, campus)
    specs = [
        # Arts, Humanities, Communications & Design
        ("Arts, Humanities, Communications & Design","Communications",                     "CRED-AA",  True, False,False,60,4,False,"CEN"),
        ("Arts, Humanities, Communications & Design","Digital Media Design & Production",  "CRED-AAS",False, True, False,63,5,False,"CEN"),
        ("Arts, Humanities, Communications & Design","Digital Media Design",               "CRED-COT",False, True, False,30,3,False,"CEN"),
        ("Arts, Humanities, Communications & Design","Fine Arts",                          "CRED-AA",  True, False,False,60,4,False,"CEN"),
        ("Arts, Humanities, Communications & Design","Music Recording",                    "CRED-AAS",False, True, False,60,4,False,"CEN"),
        ("Arts, Humanities, Communications & Design","Music",                              "CRED-AA",  True, False,False,60,4,False,"CEN"),
        # Business
        ("Business","Business",                                       "CRED-AAS",False, True, False,60,4,False,"CEN"),
        ("Business","Business",                                       "CRED-AA",  True, False,False,60,4,False,"CEN"),
        ("Business","Accounting",                                     "CRED-L2C",False, True, False,24,2,False,"CEN"),
        ("Business","Business Management",                            "CRED-COT",False, True, False,30,3,False,"CEN"),
        ("Business","Entrepreneurial and Small Business Management",  "CRED-AAS",False, True, False,60,4,False,"CEN"),
        ("Business","Logistics and Supply Chain Management",          "CRED-AAS",False, True, True, 60,4,False,"CEN"),
        ("Business","Logistics and Supply Chain Management",          "CRED-BAT",False, True, True,120,8,False,"CEN"),
        ("Business","Law and Legal Studies",                          "CRED-AAS",False, True, False,60,4,False,"CEN"),
        ("Business","Real Estate",                                    "CRED-AAS",False, True, False,60,4,False,"CEN"),
        # Construction / Industry / Manufacturing / Transportation
        ("Construction, Industry, Manufacturing & Transportation","Air Conditioning Technology",        "CRED-AAS",False,True,True, 60,4,True, "CEN"),
        ("Construction, Industry, Manufacturing & Transportation","Electrical Technology",             "CRED-AAS",False,True,True, 60,4,True, "CEN"),
        ("Construction, Industry, Manufacturing & Transportation","Welding Technology",               "CRED-AAS",False,True,True, 60,4,False,"CEN"),
        ("Construction, Industry, Manufacturing & Transportation","Process Technology",               "CRED-AAS",False,True,True, 60,4,False,"SOU"),
        ("Construction, Industry, Manufacturing & Transportation","Instrumentation Technology",       "CRED-AAS",False,True,True, 60,4,False,"SOU"),
        ("Construction, Industry, Manufacturing & Transportation","Heavy Diesel Truck",              "CRED-AAS",False,True,True, 60,4,False,"CEN"),
        ("Construction, Industry, Manufacturing & Transportation","Biomanufacturing Technology",      "CRED-AAS",False,True,True, 60,4,False,"CEN"),
        ("Construction, Industry, Manufacturing & Transportation","Maritime Transportation",         "CRED-AAS",False,True,True, 60,4,True, "MAR"),
        ("Construction, Industry, Manufacturing & Transportation","Auto Tech - Ford ASSET",          "CRED-AAS",False,True,True, 60,4,False,"CEN"),
        ("Construction, Industry, Manufacturing & Transportation","Biomedical Clinical Equipment Tech","CRED-AAS",False,True,True,60,4,False,"NOR"),
        ("Construction, Industry, Manufacturing & Transportation","Construction Management",          "CRED-AAS",False,True,True, 60,4,False,"CEN"),
        ("Construction, Industry, Manufacturing & Transportation","Environmental Health and Safety",  "CRED-AAS",False,True,True, 60,4,False,"CEN"),
        ("Construction, Industry, Manufacturing & Transportation","Pipefitting Technology",           "CRED-OCC",False,True,True, 18,2,False,"CEN"),
        ("Construction, Industry, Manufacturing & Transportation","Plumbing Technology",             "CRED-OCC",False,True,True, 18,2,False,"CEN"),
        # Education
        ("Education","Child Development / Early Childhood Education","CRED-AAS",False,True, False,60,4,False,"CEN"),
        ("Education","Early Childhood Education",                    "CRED-BAS",False,True, False,120,8,False,"CEN"),
        ("Education","Teaching (Early Childhood-6th Grade)",         "CRED-AAT",True, False,False,60,4,False,"CEN"),
        ("Education","Teaching (Grades 7-12)",                       "CRED-AAT",True, False,False,60,4,False,"CEN"),
        # Health Sciences
        ("Health Sciences","Nursing",                       "CRED-AAS",False,True,True,60,4,True, "CEN"),
        ("Health Sciences","Dental Hygiene",                "CRED-AAS",False,True,True,72,5,True, "CEN"),
        ("Health Sciences","Radiologic Technology",         "CRED-AAS",False,True,True,66,5,True, "CEN"),
        ("Health Sciences","Respiratory Care",              "CRED-AAS",False,True,True,60,4,True, "CEN"),
        ("Health Sciences","Emergency Medical Services",    "CRED-AAS",False,True,True,60,4,True, "NOR"),
        ("Health Sciences","Health Information Management", "CRED-AAS",False,True,True,60,4,True, "NOR"),
        ("Health Sciences","Cancer Data Management",        "CRED-AAS",False,True,True,60,4,True, "NOR"),
        # Information Technology
        ("Information Technology","Information Technology","CRED-AAS",False,True,True,60,4,False,"GEN"),
        ("Information Technology","Information Technology","CRED-COT",False,True,True,30,3,False,"GEN"),
        # Science & Mathematics
        ("Science & Mathematics","General Studies", "CRED-AA",True, False,False,60,4,False,"CEN"),
        ("Science & Mathematics","Pre-Engineering",  "CRED-AS",True, False,True, 60,4,False,"CEN"),
        ("Science & Mathematics","Biology",          "CRED-AS",True, False,True, 60,4,False,"CEN"),
        # Social & Behavioral Sciences
        ("Social & Behavioral Sciences","Psychology",          "CRED-AA",True,False,False,60,4,False,"CEN"),
        ("Social & Behavioral Sciences","Sociology",           "CRED-AA",True,False,False,60,4,False,"CEN"),
        ("Social & Behavioral Sciences","Behavioral Sciences", "CRED-AA",True,False,False,60,4,False,"CEN"),
        # Public Safety
        ("Public Safety & Criminal Justice","Criminal Justice","CRED-AAS",False,True,False,60,4,False,"NOR"),
        ("Public Safety & Criminal Justice","Law Enforcement", "CRED-COT",False,True,False,30,3,False,"NOR"),
    ]

    rows = []
    for i, s in enumerate(specs):
        area, name, cred_id, is_tr, is_wf, is_crit, sch_req, typ_sem, lic_req, campus = s
        rows.append({
            "program_id":                  f"PROG-{i+1:03d}",
            "program_name":                name,
            "credential_id":               cred_id,
            "area_of_study":               area,
            "is_transfer":                 is_tr,
            "is_workforce":                is_wf,
            "is_critical_field":           is_crit,
            "sch_required":                sch_req,
            "typical_completion_semesters":typ_sem,
            "licensure_required":          lic_req,
            "campus_primary":              campus,
        })
    return save(pd.DataFrame(rows), "dim_program")


def gen_dim_course():
    # (prefix, number, title, sch, is_dev, area, is_gateway)
    specs = [
        # Developmental
        ("MATH","0314","Foundations of Mathematics",           3,True, "Science & Mathematics",                             False),
        ("MATH","0332","Foundations of Math Reasoning",        3,True, "Science & Mathematics",                             False),
        ("ENGL","0305","Foundations of Writing",               3,True, "Arts, Humanities, Communications & Design",         False),
        ("READ","0306","Foundations of Reading",               3,True, "Arts, Humanities, Communications & Design",         False),
        # Math
        ("MATH","1314","College Algebra",                      3,False,"Science & Mathematics",                             True),
        ("MATH","1332","Contemporary Mathematics",             3,False,"Science & Mathematics",                             False),
        ("MATH","1342","Elementary Statistics",                3,False,"Science & Mathematics",                             False),
        ("MATH","1350","Fundamentals of Mathematics I",        3,False,"Science & Mathematics",                             False),
        ("MATH","2413","Calculus I",                           4,False,"Science & Mathematics",                             False),
        ("MATH","2414","Calculus II",                          4,False,"Science & Mathematics",                             False),
        # English / Reading
        ("ENGL","1301","Composition I",                        3,False,"Arts, Humanities, Communications & Design",         True),
        ("ENGL","1302","Composition II",                       3,False,"Arts, Humanities, Communications & Design",         False),
        ("ENGL","2322","British Literature I",                 3,False,"Arts, Humanities, Communications & Design",         False),
        ("ENGL","2327","American Literature I",                3,False,"Arts, Humanities, Communications & Design",         False),
        # Government / History
        ("GOVT","2305","Federal Government",                   3,False,"Social & Behavioral Sciences",                      False),
        ("GOVT","2306","Texas Government",                     3,False,"Social & Behavioral Sciences",                      False),
        ("HIST","1301","United States History I",              3,False,"Social & Behavioral Sciences",                      False),
        ("HIST","1302","United States History II",             3,False,"Social & Behavioral Sciences",                      False),
        # Science
        ("BIOL","1406","Biology I",                            4,False,"Science & Mathematics",                             False),
        ("BIOL","1407","Biology II",                           4,False,"Science & Mathematics",                             False),
        ("BIOL","2401","Anatomy & Physiology I",               4,False,"Science & Mathematics",                             False),
        ("BIOL","2402","Anatomy & Physiology II",              4,False,"Science & Mathematics",                             False),
        ("CHEM","1411","General Chemistry I",                  4,False,"Science & Mathematics",                             False),
        ("CHEM","1412","General Chemistry II",                 4,False,"Science & Mathematics",                             False),
        ("PHYS","1401","General Physics I",                    4,False,"Science & Mathematics",                             False),
        # Social / Behavioral
        ("PSYC","2301","General Psychology",                   3,False,"Social & Behavioral Sciences",                      False),
        ("PSYC","2314","Lifespan Development",                 3,False,"Social & Behavioral Sciences",                      False),
        ("SOCI","1301","Introduction to Sociology",            3,False,"Social & Behavioral Sciences",                      False),
        ("SOCI","1306","Social Problems",                      3,False,"Social & Behavioral Sciences",                      False),
        ("PHIL","1301","Introduction to Philosophy",           3,False,"Social & Behavioral Sciences",                      False),
        ("KINE","1301","Foundation of Kinesiology",            3,False,"Social & Behavioral Sciences",                      False),
        # Speech / Communications
        ("SPCH","1311","Introduction to Speech Communication", 3,False,"Arts, Humanities, Communications & Design",         False),
        ("COMM","1307","Introduction to Mass Communication",   3,False,"Arts, Humanities, Communications & Design",         False),
        ("COMM","1316","Photography I",                        3,False,"Arts, Humanities, Communications & Design",         False),
        # Arts / Music
        ("ARTS","1301","Art Appreciation",                     3,False,"Arts, Humanities, Communications & Design",         False),
        ("ARTS","1311","Design I",                             3,False,"Arts, Humanities, Communications & Design",         False),
        ("MUSC","1300","Music Appreciation",                   3,False,"Arts, Humanities, Communications & Design",         False),
        ("MUSC","1305","Music Theory I",                       3,False,"Arts, Humanities, Communications & Design",         False),
        # Digital Media
        ("IMED","1301","Web Design Tools",                     3,False,"Arts, Humanities, Communications & Design",         False),
        ("IMED","1345","Interactive Digital Media I",          3,False,"Arts, Humanities, Communications & Design",         False),
        ("IMED","2315","Web Design II",                        3,False,"Arts, Humanities, Communications & Design",         False),
        # Business
        ("BUSI","1301","Business Principles",                  3,False,"Business",                                          False),
        ("ACCT","2301","Principles of Accounting I",           3,False,"Business",                                          False),
        ("ACCT","2302","Principles of Accounting II",          3,False,"Business",                                          False),
        ("MKTG","1311","Principles of Marketing",              3,False,"Business",                                          False),
        ("MGMT","1370","Principles of Management",             3,False,"Business",                                          False),
        ("LGLA","1307","Introduction to Law",                  3,False,"Business",                                          False),
        ("HRPO","2301","Human Resources Management",           3,False,"Business",                                          False),
        ("BMGT","1327","Principles of Logistics",              3,False,"Business",                                          False),
        ("IBUS","1305","Introduction to International Business",3,False,"Business",                                         False),
        # Information Technology
        ("ITSC","1301","Introduction to Computers",            3,False,"Information Technology",                            False),
        ("ITSC","1325","Personal Computer Hardware",           3,False,"Information Technology",                            False),
        ("ITSE","1302","Computer Programming",                 3,False,"Information Technology",                            False),
        ("ITNW","1325","Fundamentals of Networking",           3,False,"Information Technology",                            False),
        ("ITSY","1342","Information Technology Security I",    3,False,"Information Technology",                            False),
        ("ITSE","2302","Data Structures",                      3,False,"Information Technology",                            False),
        ("ITNW","1354","Implementing & Supporting Clients",    3,False,"Information Technology",                            False),
        # Health Sciences
        ("RNSG","1105","Introduction to Nursing",              1,False,"Health Sciences",                                   False),
        ("RNSG","1413","Foundations of Nursing Practice",      4,False,"Health Sciences",                                   False),
        ("RNSG","2221","Nursing in Mental Health",             2,False,"Health Sciences",                                   False),
        ("RNSG","2362","Clinical - Registered Nursing",        3,False,"Health Sciences",                                   False),
        ("DENA","1201","Introduction to Dental Assisting",     2,False,"Health Sciences",                                   False),
        ("DENA","1341","Dental Materials",                     3,False,"Health Sciences",                                   False),
        ("DHYG","1201","Preclinical Dental Hygiene",           2,False,"Health Sciences",                                   False),
        ("RADR","1301","Introduction to Radiography",          3,False,"Health Sciences",                                   False),
        ("RADR","1313","Principles of Radiographic Imaging",   3,False,"Health Sciences",                                   False),
        ("RSPT","1329","Respiratory Care Fundamentals",        3,False,"Health Sciences",                                   False),
        ("EMSP","1501","Emergency Medical Technician",         5,False,"Health Sciences",                                   False),
        ("HITT","1305","Medical Terminology",                  3,False,"Health Sciences",                                   False),
        ("HITT","1341","Coding and Classification Systems",    3,False,"Health Sciences",                                   False),
        # Industrial / Technical
        ("PTAC","1302","Introduction to Process Technology",   3,False,"Construction, Industry, Manufacturing & Transportation",False),
        ("PTAC","1420","Process Technology I - Equipment",     4,False,"Construction, Industry, Manufacturing & Transportation",False),
        ("PTAC","2302","Process Technology II - Equipment",    3,False,"Construction, Industry, Manufacturing & Transportation",False),
        ("ELPT","1311","Introduction to Electrical Systems",   3,False,"Construction, Industry, Manufacturing & Transportation",False),
        ("ELPT","1341","Motor Controls I",                     3,False,"Construction, Industry, Manufacturing & Transportation",False),
        ("WLDG","1457","Introduction to Welding",              4,False,"Construction, Industry, Manufacturing & Transportation",False),
        ("WLDG","1430","Shielded Metal Arc Welding",           4,False,"Construction, Industry, Manufacturing & Transportation",False),
        ("AUMT","1305","Introduction to Automotive Technology",3,False,"Construction, Industry, Manufacturing & Transportation",False),
        ("AUMT","1316","Engine Repair",                        3,False,"Construction, Industry, Manufacturing & Transportation",False),
        ("MRNT","1301","Introduction to Maritime Transportation",3,False,"Construction, Industry, Manufacturing & Transportation",False),
        ("MRNT","1341","Vessel Operations",                    3,False,"Construction, Industry, Manufacturing & Transportation",False),
        ("MATR","1313","Introduction to Biomanufacturing",     3,False,"Construction, Industry, Manufacturing & Transportation",False),
        ("MATR","1411","Biomanufacturing Technology I",        4,False,"Construction, Industry, Manufacturing & Transportation",False),
        ("HVAC","1345","Air Conditioning and Refrigeration I", 3,False,"Construction, Industry, Manufacturing & Transportation",False),
        ("CNBT","1302","Construction Technology",              3,False,"Construction, Industry, Manufacturing & Transportation",False),
        ("INTC","1305","Introduction to Instrumentation",      3,False,"Construction, Industry, Manufacturing & Transportation",False),
        # Education
        ("CDEC","1313","Child Development",                    3,False,"Education",                                         False),
        ("CDEC","1356","Emergent Literacy for Early Childhood",3,False,"Education",                                         False),
        ("EDUC","1301","Introduction to Teaching",             3,False,"Education",                                         False),
        ("EDUC","2301","Introduction to Special Populations",  3,False,"Education",                                         False),
        # Criminal Justice
        ("CRIJ","1301","Introduction to Criminal Justice",     3,False,"Public Safety & Criminal Justice",                  False),
        ("CRIJ","1307","Crime in America",                     3,False,"Public Safety & Criminal Justice",                  False),
        ("CRIJ","2314","Criminal Investigation",               3,False,"Public Safety & Criminal Justice",                  False),
    ]

    rows = []
    for s in specs:
        prefix, number, title, sch, is_dev, area, is_gw = s
        rows.append({
            "course_id":       f"{prefix}-{number}",
            "course_prefix":   prefix,
            "course_number":   number,
            "course_title":    title,
            "sch_value":       sch,
            "course_level":    "Developmental" if is_dev else "College-Level",
            "area_of_study":   area,
            "is_gateway":      is_gw,
            "is_developmental":is_dev,
        })
    df = pd.DataFrame(rows).drop_duplicates(subset="course_id")
    return save(df, "dim_course")


def gen_dim_student(programs_df):
    ethnicities = [
        "Hispanic or Latino","White","Black or African American","Asian",
        "Two or More Races","Unknown / Not Reported",
        "American Indian / Alaska Native","Native Hawaiian / Pacific Islander",
    ]
    eth_w = [63.3, 15.2, 8.5, 5.0, 1.9, 5.1, 0.6, 0.4]

    age_brackets = [(15,17),(18,21),(22,25),(26,35),(36,50),(51,70)]
    age_w        = [5, 45, 20, 18, 10, 2]

    program_ids = programs_df["program_id"].tolist()

    # Distribute cohort terms realistically across 3 AYs
    cohort_terms = ["2022FA","2023SP","2023SU","2023FA","2024SP","2024SU","2024FA","2025SP","2025FA"]
    cohort_w     = [18, 9, 3, 18, 9, 3, 18, 9, 13]

    rows = []
    for i in range(N_STUDENTS):
        sid      = f"S{i+1:06d}"
        gender   = wchoice(["Female","Male"], [59, 41])
        ethnicity= wchoice(ethnicities, eth_w)

        # Correlated Pell & first-gen by ethnicity
        if ethnicity == "Hispanic or Latino":
            pell      = random.random() < 0.65
            first_gen = random.random() < 0.50
        elif ethnicity in ("Black or African American",):
            pell      = random.random() < 0.68
            first_gen = random.random() < 0.48
        elif ethnicity == "White":
            pell      = random.random() < 0.35
            first_gen = random.random() < 0.30
        else:
            pell      = random.random() < 0.45
            first_gen = random.random() < 0.38

        # Age
        ab  = wchoice(age_brackets, age_w)
        age = random.randint(ab[0], ab[1])
        dual_credit = (age < 18) and (random.random() < 0.80)

        # Name
        if ethnicity == "Hispanic or Latino":
            fn = random.choice(HISP_FIRST_F if gender == "Female" else HISP_FIRST_M)
            ln = random.choice(HISP_LAST)
        else:
            fn = fake.first_name_female() if gender == "Female" else fake.first_name_male()
            ln = fake.last_name()

        # Location (97% TX)
        z = random.random()
        if z < 0.80:
            zip_code, state = random.choice(SJC_ZIPS), "TX"
        elif z < 0.97:
            zip_code, state = random.choice(TX_OTHER_ZIPS), "TX"
        else:
            zip_code = random.choice(OOS_ZIPS)
            state    = wchoice(["CA","GA","IL","NY","AZ","WA"], [2,1,1,1,1,1])

        # TSI (correlated with dual credit / academic preparation)
        tsi_math    = random.random() < (0.90 if dual_credit else 0.65)
        tsi_reading = random.random() < (0.92 if dual_credit else 0.70)

        # Admissions checklist (only meaningful for applicants who proceed)
        meningitis = random.random() < 0.85
        nso        = random.random() < 0.80

        cohort_term = wchoice(cohort_terms, cohort_w)
        hs_gpa      = round(float(np.clip(np.random.normal(2.8, 0.5), 1.5, 4.0)), 2)
        isd         = random.choice(FEEDER_ISDS)
        program_id  = random.choice(program_ids)

        # Cohort start date ~ 30 days before term start
        t_start = TERM_META[cohort_term][2]
        created = t_start - timedelta(days=random.randint(10, 45))

        rows.append({
            "student_id":              sid,
            "first_name":              fn,
            "last_name":               ln,
            "gender":                  gender,
            "ethnicity":               ethnicity,
            "age_at_first_enrollment": age,
            "dob":                     date(t_start.year - age, random.randint(1,12), random.randint(1,28)),
            "zip_code":                zip_code,
            "state":                   state,
            "pell_eligible":           pell,
            "first_gen_college":       first_gen,
            "high_school_district":    isd,
            "dual_credit":             dual_credit,
            "hs_gpa":                  hs_gpa,
            "tsi_math_exempt":         tsi_math,
            "tsi_reading_exempt":      tsi_reading,
            "meningitis_submitted":    meningitis,
            "nso_complete":            nso,
            "cohort_term_id":          cohort_term,
            "program_id":              program_id,
            "created_date":            created,
        })

    return save(pd.DataFrame(rows), "dim_student")


# ─────────────────────────────────────────────────────────────────────────────
# ENROLLMENT SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

def _persist_prob(season_from, season_to, is_ft, has_aid, pell, prev_gpa):
    """Base persistence probability between two consecutive terms."""
    if season_to == "Summer":
        base = 0.35
    elif season_from == "Fall" and season_to == "Spring":
        base = 0.68
    elif season_from in ("Spring","Summer") and season_to == "Fall":
        base = 0.62
    else:
        base = 0.55

    if is_ft:    base = min(base + 0.10, 0.95)
    if has_aid:  base = min(base + 0.05, 0.95)
    if pell:     base = base * 0.96          # slight financial instability
    if prev_gpa is not None:
        if prev_gpa >= 3.0:   base = min(base + 0.06, 0.95)
        elif prev_gpa < 2.0:  base = base * 0.85
    return base


def simulate_enrollments(students_df, programs_df):
    """
    For each student, simulate which terms they enrolled in from cohort through
    current. Returns a list of (student_id, term_id, enrollment_type, is_ft,
    has_aid, stage_id, withdrew_term, cumulative_sch_before) dicts.
    """
    prog_map = programs_df.set_index("program_id")[
        ["sch_required","typical_completion_semesters","is_transfer"]
    ].to_dict("index")

    enrollments = []

    for _, stu in students_df.iterrows():
        sid         = stu["student_id"]
        cohort_idx  = TERM_IDX[stu["cohort_term_id"]]
        pell        = stu["pell_eligible"]
        age         = stu["age_at_first_enrollment"]
        prog        = prog_map.get(stu["program_id"], {"sch_required":60,"typical_completion_semesters":4,"is_transfer":False})
        sch_req     = prog["sch_required"]

        # Student enrollment profile
        # Online-only probability: correlated with age >25 and pell
        online_prob = 0.42 if age > 25 else 0.22
        is_online   = random.random() < online_prob

        # Full-time probability: correlated with age and pell
        ft_prob = 0.27 if (pell or age > 25 or is_online) else 0.55
        is_ft   = random.random() < ft_prob

        # Persistence profile (determines overall tendency to stay enrolled)
        persist_profile = wchoice(["high","medium","low","dropout"],[30,45,20,5])

        profile_adj = {"high": 0.12, "medium": 0.0, "low": -0.12, "dropout": -0.30}[persist_profile]

        has_aid   = pell or (random.random() < 0.10)  # some non-Pell students get aid
        cum_sch   = 0
        prev_gpa  = None
        gap_terms = 0       # consecutive terms without enrollment
        graduated = False
        current_stage = None

        for tidx in range(cohort_idx, len(TERM_ORDER)):
            tid    = TERM_ORDER[tidx]
            season = TERM_META[tid][0]

            # First term: always enroll (they're in the system)
            if tidx == cohort_idx:
                enroll = True
            else:
                prev_tid    = TERM_ORDER[tidx - 1]
                prev_season = TERM_META[prev_tid][0]
                p = _persist_prob(prev_season, season, is_ft, has_aid, pell, prev_gpa)
                p = clamp(p + profile_adj, 0.05, 0.97)
                enroll = random.random() < p

            if not enroll:
                gap_terms += 1
                if gap_terms >= 3:
                    current_stage = 10  # Stop-Out
                    break
                continue

            gap_terms = 0

            # SCH this term
            if is_ft:
                sch = wchoice([12,13,14,15,16], [30,30,20,15,5])
            else:
                sch = wchoice([3,4,5,6,7,8,9,10,11], [8,7,10,18,15,15,12,8,7])

            # Enrollment type
            if tidx == cohort_idx:
                enrollment_type = wchoice(
                    ["First-Time-in-College","Transfer","Re-admit"],
                    [75, 20, 5]
                )
            else:
                enrollment_type = "Continuing"

            # Stage at census
            if tid == CURRENT_TERM:
                stage_id = wchoice([8,6,7,5,4],[62,4,8,4,3])
            else:
                # Historical: mostly enrolled (8)
                stage_id = wchoice([8,10,9],[88,7,5])

            # Payment status consistent with stage
            if stage_id == 6:    payment = "Unpaid"
            elif has_aid:        payment = wchoice(["Aid Authorized","Paid","Payment Plan"],[60,30,10])
            else:                payment = wchoice(["Paid","Payment Plan"],[70,30])

            # Withdrew from all courses this term (8%)
            withdrew_term = (random.random() < 0.08) and (stage_id == 8)

            # SCH completed (if withdrew: 0; else roughly sch * success rate)
            if withdrew_term:
                sch_completed = 0
            else:
                success_rate = 0.72
                if is_ft:       success_rate += 0.05
                if has_aid:     success_rate += 0.03
                if pell:        success_rate -= 0.02
                if enrollment_type == "First-Time-in-College": success_rate -= 0.05
                success_rate = clamp(success_rate, 0.40, 0.95)
                sch_completed = round(sch * success_rate)

            sch_on_pathway = round(sch_completed * random.uniform(0.80, 0.95))
            cum_sch += sch_completed

            # Graduation check: near end of program
            if (cum_sch >= sch_req * 0.90
                    and tidx >= cohort_idx + prog["typical_completion_semesters"] - 1
                    and not graduated):
                grad_prob = 0.60 if stu.get("licensure_required", False) else 0.75
                if random.random() < grad_prob:
                    graduated  = True
                    stage_id   = 9  # Graduate/Alumni

            # Term GPA for persistence calc
            if sch_completed > 0:
                prev_gpa = round(random.uniform(1.5, 4.0), 2) if withdrew_term else round(
                    clamp(np.random.normal(2.6 if not is_ft else 2.9, 0.7), 0.0, 4.0), 2
                )

            enrollments.append({
                "student_id":        sid,
                "term_id":           tid,
                "program_id":        stu["program_id"],
                "enrollment_type":   enrollment_type,
                "is_ft":             is_ft,
                "is_online_only":    is_online,
                "has_some_online":   (not is_online) and (random.random() < 0.32),
                "payment_status":    payment,
                "stage_id":          stage_id,
                "total_sch_attempted":sch,
                "total_sch_completed":sch_completed,
                "sch_on_pathway":    sch_on_pathway,
                "mf_hold_active":    stage_id == 4,
                "is_first_term":     tidx == cohort_idx,
                "withdrew_term":     withdrew_term,
                "financial_aid_term":has_aid,
                "pell_eligible":     pell,
                "term_gpa":          prev_gpa,
                "graduated":         graduated and stage_id == 9,
            })

            if graduated:
                break

    return enrollments


# ── Fact: Enrollment ──────────────────────────────────────────────────────────

def gen_fact_enrollment(enrollments, campus_ids):
    rows = []
    for i, e in enumerate(enrollments):
        campus = wchoice(campus_ids, [45,20,20,10,5])
        rows.append({
            "enrollment_id":       i + 1,
            "student_id":          e["student_id"],
            "term_id":             e["term_id"],
            "program_id":          e["program_id"],
            "campus_id":           campus,
            "stage_id":            e["stage_id"],
            "enrollment_type":     e["enrollment_type"],
            "total_sch_attempted": e["total_sch_attempted"],
            "total_sch_completed": e["total_sch_completed"],
            "sch_on_pathway":      e["sch_on_pathway"],
            "is_online_only":      e["is_online_only"],
            "has_some_online":     e["has_some_online"],
            "payment_status":      e["payment_status"],
            "mf_hold_active":      e["mf_hold_active"],
            "is_first_term":       e["is_first_term"],
            "withdrew_term":       e["withdrew_term"],
            "financial_aid_term":  e["financial_aid_term"],
        })
    return save(pd.DataFrame(rows), "fact_enrollment")


# ── Fact: Course Attempt ──────────────────────────────────────────────────────

def gen_fact_course_attempt(enrollments, courses_df, campus_ids):
    # Map area → course_ids for realistic course assignment
    area_courses = courses_df.groupby("area_of_study")["course_id"].apply(list).to_dict()
    dev_courses  = courses_df[courses_df["is_developmental"]]["course_id"].tolist()
    core_courses = courses_df[
        courses_df["course_prefix"].isin(["GOVT","HIST","ENGL","MATH","SPCH"])
        & ~courses_df["is_developmental"]
    ]["course_id"].tolist()

    # Programs → area mapping (approximate via program_id prefix not available here — use cohort)
    grade_map = {"A":4.0,"B":3.0,"C":2.0,"D":1.0,"F":0.0}
    delivery_modes = ["Face-to-face","Online","Hybrid"]
    delivery_w     = [38, 30, 32]

    rows = []
    attempt_id = 1

    for e in enrollments:
        if e["stage_id"] not in (8, 9):
            continue  # only generate course attempts for enrolled/graduated
        if e["withdrew_term"]:
            n_courses = wchoice([1,2,3],[40,35,25])
        else:
            sch = e["total_sch_attempted"]
            n_courses = max(1, round(sch / 3))

        for c in range(n_courses):
            # Course selection: dev ed in first term for some FTIC students
            is_dev = (e["is_first_term"]
                      and e["enrollment_type"] == "First-Time-in-College"
                      and c == 0
                      and random.random() < 0.30)

            if is_dev and dev_courses:
                course_id = random.choice(dev_courses)
            elif c == 0 and core_courses:
                course_id = random.choice(core_courses)
            else:
                course_id = random.choice(courses_df["course_id"].tolist())

            course_row   = courses_df[courses_df["course_id"] == course_id].iloc[0]
            is_dev_course= bool(course_row["is_developmental"])
            sch_val      = int(course_row["sch_value"])
            delivery     = wchoice(delivery_modes, delivery_w)

            # Attendance — correlated with ft, online
            att_mean = 86 if not e["is_online_only"] else 78
            att_sd   = 12
            att_pct  = round(clamp(np.random.normal(att_mean, att_sd), 0, 100), 1)

            # Withdrawal probability
            w_base = 0.14 if is_dev_course else 0.05
            if e["is_first_term"]:     w_base += 0.03
            if e["is_online_only"]:    w_base += 0.03
            if e["financial_aid_term"]:w_base -= 0.03
            withdrew = (random.random() < clamp(w_base, 0.05, 0.40)) or e["withdrew_term"]

            if withdrew:
                grade, grade_pts, ac_success, sch_earned = "W", None, False, 0
            else:
                # Grade — correlated with attendance, dev, ft, aid
                if att_pct < 65:
                    g_w = [5, 8, 12, 20, 55]   # A,B,C,D,F
                elif is_dev_course:
                    g_w = [20,15, 20,15, 30]
                elif e["is_ft"]:
                    g_w = [40,25, 15, 8, 12]
                elif e["financial_aid_term"]:
                    g_w = [38,24, 15, 8, 15]
                else:
                    g_w = [35,22, 15, 8, 20]

                grade_letter = wchoice(["A","B","C","D","F"], g_w)
                grade        = grade_letter
                grade_pts    = grade_map[grade_letter]
                ac_success   = grade_letter in ("A","B","C")
                sch_earned   = sch_val if grade_letter not in ("F",) else 0

            # Midterm grade (leading indicator — slightly worse than final on average)
            if withdrew:
                midterm = wchoice(["C","D","F"],[20,35,45])
            else:
                midterm_drift = {"A":"A","B":wchoice(["A","B"],[30,70]),"C":wchoice(["B","C"],[20,80]),
                                 "D":wchoice(["C","D"],[20,80]),"F":"F"}.get(grade, grade)
                midterm = midterm_drift

            section_id  = f"{course_id}-{e['term_id']}-{random.randint(100,599):03d}"
            instructor  = f"INST-{random.randint(1,400):04d}"
            campus      = wchoice(campus_ids,[45,20,20,10,5])

            rows.append({
                "attempt_id":     attempt_id,
                "student_id":     e["student_id"],
                "term_id":        e["term_id"],
                "course_id":      course_id,
                "campus_id":      campus,
                "section_id":     section_id,
                "delivery_mode":  delivery,
                "instructor_id":  instructor,
                "grade":          grade,
                "grade_points":   grade_pts,
                "ac_success":     ac_success,
                "withdrew":       withdrew,
                "sch_earned":     sch_earned,
                "is_developmental":is_dev_course,
                "attendance_pct": att_pct,
                "midterm_grade":  midterm,
            })
            attempt_id += 1

    return save(pd.DataFrame(rows), "fact_course_attempt")


# ── Fact: Financial Aid ───────────────────────────────────────────────────────

def gen_fact_financial_aid(enrollments, students_df):
    stu_map = students_df.set_index("student_id")["pell_eligible"].to_dict()
    prog_map= students_df.set_index("student_id")["program_id"].to_dict()

    # Workforce programs eligible for Workforce Solutions aid
    workforce_progs = set()  # populated below from programs_df if needed; keep simple

    rows = []
    aid_id = 1

    for e in enrollments:
        sid  = e["student_id"]
        pell = stu_map.get(sid, False)

        if not e["financial_aid_term"]:
            continue

        # SAP
        sap = random.random() < 0.85

        # Unmet need
        unmet = wchoice([0, 200, 800, 2000, 4000], [20,25,30,15,10])
        unmet = round(float(unmet) + random.uniform(-50, 50), 2) if unmet > 0 else 0.0

        # Pell Grant
        if pell:
            award  = round(random.uniform(2800, 3600), 2)
            disb   = award if sap else 0.0
            status = "Disbursed" if sap else "Cancelled"
            rows.append({
                "aid_id":                         aid_id,
                "student_id":                     sid,
                "term_id":                        e["term_id"],
                "aid_type":                       "Pell Grant",
                "aid_amount_awarded":             award,
                "aid_amount_disbursed":           disb,
                "unmet_need":                     unmet,
                "disbursement_status":            status,
                "satisfactory_academic_progress": sap,
                "enrollment_intensity_required":  6,
                "cumulative_loan_balance":        None,
            })
            aid_id += 1

            # TPEG — 15% of Pell students
            if random.random() < 0.15:
                t_award = round(random.uniform(300, 1200), 2)
                rows.append({
                    "aid_id":                         aid_id,
                    "student_id":                     sid,
                    "term_id":                        e["term_id"],
                    "aid_type":                       "TPEG",
                    "aid_amount_awarded":             t_award,
                    "aid_amount_disbursed":           t_award if sap else 0.0,
                    "unmet_need":                     max(0, unmet - t_award),
                    "disbursement_status":            "Disbursed" if sap else "Cancelled",
                    "satisfactory_academic_progress": sap,
                    "enrollment_intensity_required":  3,
                    "cumulative_loan_balance":        None,
                })
                aid_id += 1

        # Institutional Grant — 10%
        if random.random() < 0.10:
            ig = round(random.uniform(200, 800), 2)
            rows.append({
                "aid_id":                         aid_id,
                "student_id":                     sid,
                "term_id":                        e["term_id"],
                "aid_type":                       "Institutional Grant",
                "aid_amount_awarded":             ig,
                "aid_amount_disbursed":           ig,
                "unmet_need":                     max(0, unmet - ig),
                "disbursement_status":            "Disbursed",
                "satisfactory_academic_progress": sap,
                "enrollment_intensity_required":  6,
                "cumulative_loan_balance":        None,
            })
            aid_id += 1

        # Student Loan — 12%
        if random.random() < 0.12:
            loan   = round(random.uniform(1000, 3500), 2)
            cum_lb = round(random.uniform(loan, loan * 5), 2)
            rows.append({
                "aid_id":                         aid_id,
                "student_id":                     sid,
                "term_id":                        e["term_id"],
                "aid_type":                       "Student Loan",
                "aid_amount_awarded":             loan,
                "aid_amount_disbursed":           loan,
                "unmet_need":                     max(0, unmet - loan),
                "disbursement_status":            "Disbursed",
                "satisfactory_academic_progress": sap,
                "enrollment_intensity_required":  6,
                "cumulative_loan_balance":        cum_lb,
            })
            aid_id += 1

        # Work-Study — 3%
        if random.random() < 0.03:
            ws = round(random.uniform(500, 1500), 2)
            rows.append({
                "aid_id":                         aid_id,
                "student_id":                     sid,
                "term_id":                        e["term_id"],
                "aid_type":                       "Work-Study",
                "aid_amount_awarded":             ws,
                "aid_amount_disbursed":           ws,
                "unmet_need":                     max(0, unmet - ws),
                "disbursement_status":            "Disbursed",
                "satisfactory_academic_progress": sap,
                "enrollment_intensity_required":  6,
                "cumulative_loan_balance":        None,
            })
            aid_id += 1

    return save(pd.DataFrame(rows), "fact_financial_aid")


# ── Fact: Student Stage History ───────────────────────────────────────────────

def gen_fact_student_stage_history(students_df, enrollments):
    """
    Reconstruct a stage journey per student based on their enrollment pattern.
    """
    # Group enrollments per student, sorted by term
    from collections import defaultdict
    stu_terms = defaultdict(list)
    for e in enrollments:
        stu_terms[e["student_id"]].append(e)
    for sid in stu_terms:
        stu_terms[sid].sort(key=lambda x: TERM_IDX[x["term_id"]])

    rows = []
    hist_id = 1

    for _, stu in students_df.iterrows():
        sid          = stu["student_id"]
        cohort_term  = stu["cohort_term_id"]
        t_start      = TERM_META[cohort_term][2]
        enrolments   = stu_terms.get(sid, [])

        # --- Stage 1: Prospective (inquiry, 10–40 days before cohort term start)
        prosp_start = t_start - timedelta(days=random.randint(10, 40))
        prosp_end   = prosp_start + timedelta(days=random.randint(5, 14))

        rows.append({"history_id":hist_id,"student_id":sid,"stage_id":1,
                     "stage_start_date":prosp_start,"stage_end_date":prosp_end,
                     "days_in_stage":(prosp_end-prosp_start).days,"previous_stage_id":None,
                     "trigger_type":"Record-Triggered","term_id":cohort_term})
        hist_id += 1

        # --- 8% → Not Interested
        if random.random() < 0.08:
            ni_start = prosp_end + timedelta(days=random.randint(1, 5))
            ni_end   = None
            rows.append({"history_id":hist_id,"student_id":sid,"stage_id":3,
                         "stage_start_date":ni_start,"stage_end_date":ni_end,
                         "days_in_stage":None,"previous_stage_id":1,
                         "trigger_type":"Record-Triggered","term_id":cohort_term})
            hist_id += 1
            continue   # stop journey

        # --- Stage 2: Applicant
        app_start = prosp_end
        app_end   = app_start + timedelta(days=random.randint(7, 21))
        rows.append({"history_id":hist_id,"student_id":sid,"stage_id":2,
                     "stage_start_date":app_start,"stage_end_date":app_end,
                     "days_in_stage":(app_end-app_start).days,"previous_stage_id":1,
                     "trigger_type":"Record-Triggered","term_id":cohort_term})
        hist_id += 1

        # --- Stage 4: Admitted
        adm_start = app_end + timedelta(days=random.randint(1, 7))
        adm_end   = adm_start + timedelta(days=random.randint(3, 14))
        rows.append({"history_id":hist_id,"student_id":sid,"stage_id":4,
                     "stage_start_date":adm_start,"stage_end_date":adm_end,
                     "days_in_stage":(adm_end-adm_start).days,"previous_stage_id":2,
                     "trigger_type":"Record-Triggered","term_id":cohort_term})
        hist_id += 1

        # --- 15% → Recruit Backs (stalled at Eligible to Register - New)
        if not enrolments and random.random() < 0.15:
            rb_start = adm_end + timedelta(days=random.randint(1, 5))
            rb_end   = None
            rows.append({"history_id":hist_id,"student_id":sid,"stage_id":11,
                         "stage_start_date":rb_start,"stage_end_date":rb_end,
                         "days_in_stage":None,"previous_stage_id":4,
                         "trigger_type":"Date-Based","term_id":cohort_term})
            hist_id += 1
            continue

        # --- Stage 5: Eligible to Register - New
        elig_start = adm_end
        elig_end   = elig_start + timedelta(days=random.randint(2, 7))
        rows.append({"history_id":hist_id,"student_id":sid,"stage_id":5,
                     "stage_start_date":elig_start,"stage_end_date":elig_end,
                     "days_in_stage":(elig_end-elig_start).days,"previous_stage_id":4,
                     "trigger_type":"Record-Triggered","term_id":cohort_term})
        hist_id += 1

        # --- For each enrolled term, add Register Pending → Enrolled transitions
        prev_stage = 5
        prev_end   = elig_end

        for idx, e in enumerate(enrolments):
            t_meta = TERM_META[e["term_id"]]

            # Register Pending
            rp_start = prev_end + timedelta(days=random.randint(1, 5))
            rp_end   = rp_start + timedelta(days=random.randint(1, 4))
            rows.append({"history_id":hist_id,"student_id":sid,"stage_id":6,
                         "stage_start_date":rp_start,"stage_end_date":rp_end,
                         "days_in_stage":(rp_end-rp_start).days,"previous_stage_id":prev_stage,
                         "trigger_type":"Record-Triggered","term_id":e["term_id"]})
            hist_id += 1

            # Enrolled
            enr_start = rp_end + timedelta(days=random.randint(0, 3))
            # End date: 4 weeks before term end (trigger to Continuing) or graduation
            term_end  = t_meta[3]
            enr_end   = term_end - timedelta(weeks=4)
            rows.append({"history_id":hist_id,"student_id":sid,"stage_id":8,
                         "stage_start_date":enr_start,"stage_end_date":enr_end,
                         "days_in_stage":(enr_end-enr_start).days,"previous_stage_id":6,
                         "trigger_type":"Record-Triggered","term_id":e["term_id"]})
            hist_id += 1

            if e.get("graduated"):
                # Graduate/Alumni
                grad_date = term_end + timedelta(days=random.randint(1, 14))
                rows.append({"history_id":hist_id,"student_id":sid,"stage_id":9,
                             "stage_start_date":grad_date,"stage_end_date":None,
                             "days_in_stage":None,"previous_stage_id":8,
                             "trigger_type":"Record-Triggered","term_id":e["term_id"]})
                hist_id += 1
                break

            # Eligible to Register - Continuing (date-based, 4 wks before term end)
            cont_start = enr_end
            cont_end   = cont_start + timedelta(days=random.randint(30, 90))
            rows.append({"history_id":hist_id,"student_id":sid,"stage_id":7,
                         "stage_start_date":cont_start,"stage_end_date":cont_end,
                         "days_in_stage":(cont_end-cont_start).days,"previous_stage_id":8,
                         "trigger_type":"Date-Based","term_id":e["term_id"]})
            hist_id += 1
            prev_stage = 7
            prev_end   = cont_end

        # Check for Stop-Out (if last enrollment was 3+ terms ago)
        if enrolments:
            last_term = enrolments[-1]["term_id"]
            last_idx  = TERM_IDX[last_term]
            curr_idx  = TERM_IDX[CURRENT_TERM]
            if not enrolments[-1].get("graduated") and (curr_idx - last_idx) >= 3:
                so_start = TERM_META[last_term][3] + timedelta(days=random.randint(30,90))
                rows.append({"history_id":hist_id,"student_id":sid,"stage_id":10,
                             "stage_start_date":so_start,"stage_end_date":None,
                             "days_in_stage":None,"previous_stage_id":7,
                             "trigger_type":"Date-Based","term_id":last_term})
                hist_id += 1

    return save(pd.DataFrame(rows), "fact_student_stage_history")


# ── Fact: CPD Enrollment ──────────────────────────────────────────────────────

def gen_dim_cpd_student():
    rows = []
    for i in range(N_CPD):
        age = random.randint(18, 65)
        rows.append({
            "cpd_student_id": f"CPD{i+1:05d}",
            "first_name":     fake.first_name(),
            "last_name":      fake.last_name(),
            "age":            age,
            "zip_code":       random.choice(SJC_ZIPS + TX_OTHER_ZIPS),
            "employer_name":  fake.company() if random.random() < 0.55 else None,
        })
    return save(pd.DataFrame(rows), "dim_cpd_student")


def gen_fact_cpd_enrollment(cpd_students_df, campus_ids):
    cpd_courses = [
        # (code, name, center)
        ("EDGE-101","FAA Part 107 Drone Pilot Certification","EDGE"),
        ("EDGE-102","Composite Manufacturing Fundamentals","EDGE"),
        ("EDGE-103","Aerospace Quality Technician Training","EDGE"),
        ("EDGE-104","Aircraft Structure Technology","EDGE"),
        ("BIT-101","Introduction to Artificial Intelligence","BIT"),
        ("BIT-102","Python for Data Analysis","BIT"),
        ("BIT-103","Supply Chain Analytics","BIT"),
        ("BIT-104","Business Intelligence Fundamentals","BIT"),
        ("BIT-105","Cybersecurity Essentials","BIT"),
        ("CORP-101","OSHA 30-Hour Safety Training","Corporate"),
        ("CORP-102","Project Management Professional Prep","Corporate"),
        ("CORP-103","Lean Six Sigma Yellow Belt","Corporate"),
        ("CORP-104","Forklift Operator Certification","Corporate"),
        ("CH-101","Phlebotomy Technician","Community & Health"),
        ("CH-102","Medical Administrative Assistant","Community & Health"),
        ("CH-103","EKG Technician","Community & Health"),
        ("CH-104","ESL Beginning A","Community & Health"),
        ("CH-105","ESL Advanced B","Community & Health"),
        ("CH-106","Conversational English","Community & Health"),
        ("CH-107","CPR / First Aid","Community & Health"),
        ("CH-108","Adult Basic Education","Community & Health"),
    ]
    center_weights = {"EDGE":18,"BIT":25,"Corporate":22,"Community & Health":35}
    cpd_ids = cpd_students_df["cpd_student_id"].tolist()
    completion_statuses = ["Completed","In Progress","Dropped","No-Show"]
    completion_w        = [78, 2, 12, 8]

    rows = []
    for i, cid in enumerate(cpd_ids):
        # Each CPD student takes 1–3 courses
        n = random.choices([1,2,3],[55,30,15])[0]
        for _ in range(n):
            c_code, c_name, center = random.choice(cpd_courses)
            term  = wchoice(TERM_ORDER[2:], [1]*len(TERM_ORDER[2:]))
            t_start = TERM_META[term][2]
            enr_date = rand_date_between(t_start - timedelta(days=30), t_start + timedelta(days=14))
            rows.append({
                "cpd_enrollment_id":  i * 3 + _ + 1,
                "cpd_student_id":     cid,
                "term_id":            term,
                "course_id":          c_code,
                "course_name":        c_name,
                "cpd_center":         center,
                "campus_id":          wchoice(campus_ids,[45,20,20,10,5]),
                "delivery_mode":      wchoice(["In-Person","Online","Hybrid"],[50,30,20]),
                "enrollment_date":    enr_date,
                "completion_status":  wchoice(completion_statuses, completion_w),
                "seat_capacity":      random.choice([12,15,20,24,30]),
                "grant_funded":       random.random() < 0.25,
                "employer_sponsored": random.random() < 0.20,
                "linked_to_credit":   random.random() < 0.10,
            })
    return save(pd.DataFrame(rows), "fact_cpd_enrollment")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\nSan Jacinto College — Synthetic Data Generator")
    print("=" * 52)
    print(f"Seed: {SEED}  |  Students: {N_STUDENTS:,}  |  CPD: {N_CPD:,}")
    print(f"Output: {OUTPUT_DIR.resolve()}\n")

    print("── Dimensions ──────────────────────────────────")
    campus_df     = gen_dim_campus()
    stage_df      = gen_dim_stage()
    cred_df       = gen_dim_credential()
    term_df       = gen_dim_term()
    program_df    = gen_dim_program()
    course_df     = gen_dim_course()
    student_df    = gen_dim_student(program_df)
    cpd_student_df= gen_dim_cpd_student()

    campus_ids = campus_df["campus_id"].tolist()

    print("\n── Simulating student journeys ─────────────────")
    enrollments = simulate_enrollments(student_df, program_df)
    print(f"  →  {len(enrollments):,} enrollment records generated")

    print("\n── Facts ───────────────────────────────────────")
    gen_fact_enrollment(enrollments, campus_ids)
    gen_fact_course_attempt(enrollments, course_df, campus_ids)
    gen_fact_financial_aid(enrollments, student_df)
    gen_fact_student_stage_history(student_df, enrollments)
    gen_fact_cpd_enrollment(cpd_student_df, campus_ids)

    print("\n── Validation Targets ──────────────────────────")
    enr_df = pd.read_csv(OUTPUT_DIR / "fact_enrollment.csv")
    stu_df = pd.read_csv(OUTPUT_DIR / "dim_student.csv")
    cur_enr = enr_df[enr_df["term_id"] == CURRENT_TERM]

    print(f"  Pell eligible rate:    {stu_df['pell_eligible'].mean():.1%}  (target 56%)")
    print(f"  Hispanic rate:         {(stu_df['ethnicity']=='Hispanic or Latino').mean():.1%}  (target 63.3%)")
    print(f"  Female rate:           {(stu_df['gender']=='Female').mean():.1%}  (target 59%)")
    print(f"  Full-time rate:        {(enr_df['total_sch_attempted']>=12).mean():.1%}  (target 33.8%)")
    print(f"  Online-only rate:      {enr_df['is_online_only'].mean():.1%}  (target 30%)")
    print(f"  Term withdrawal rate:  {enr_df['withdrew_term'].mean():.1%}  (target ~8%)")

    att_df = pd.read_csv(OUTPUT_DIR / "fact_course_attempt.csv")
    non_w  = att_df[att_df["withdrew"] == False]
    print(f"  A-C success rate:      {non_w['ac_success'].mean():.1%}  (target ~72%)")
    print(f"  Course W rate:         {att_df['withdrew'].mean():.1%}  (target ~12%)")

    print(f"\n  Total enrollment rows: {len(enr_df):,}")
    print(f"  Total course attempts: {len(att_df):,}")
    print(f"\nDone. CSVs written to {OUTPUT_DIR.resolve()}\n")


if __name__ == "__main__":
    main()
