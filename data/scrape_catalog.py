"""
San Jacinto College — Course Catalog Scraper
=============================================
Scrapes the official SJC catalog at publications.sanjac.edu and writes
a structured Markdown file to docs/course-catalog.md for use with
Snowflake Cortex Search.

Usage:
    pip install requests beautifulsoup4
    python data/scrape_catalog.py

Output: docs/course-catalog.md  (~3,000+ courses)
"""

import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://publications.sanjac.edu"
OUTPUT   = Path(__file__).parent.parent / "docs" / "course-catalog.md"
DELAY    = 0.4   # seconds between requests (be polite)

# ── All subject areas from /courses-az/ ──────────────────────────────────────

SUBJECTS = [
    ("Accounting",                  "ACCT",  "/courses-az/acct/"),
    ("Accounting",                  "ACNT",  "/courses-az/acnt/"),
    ("Air Conditioning Tech",       "EECT",  "/courses-az/eect-ac/"),
    ("Air Conditioning Tech",       "HART",  "/courses-az/hart/"),
    ("American Sign Language",      "SGNL",  "/courses-az/sgnl/"),
    ("Anthropology",                "ANTH",  "/courses-az/anth/"),
    ("Applied Mathematics",         "TECM",  "/courses-az/tecm/"),
    ("Applied Physical Science",    "SCIT",  "/courses-az/scit/"),
    ("Art",                         "ARTC",  "/courses-az/artc/"),
    ("Art",                         "ARTS",  "/courses-az/arts/"),
    ("Art",                         "ARTV",  "/courses-az/artv/"),
    ("Astronomy",                   "ASTR",  "/courses-az/astr/"),
    ("Audio Engineering",           "MUSB",  "/courses-az/musb/"),
    ("Audio Engineering",           "MUSC",  "/courses-az/musc/"),
    ("Automotive Technology",       "AUMT",  "/courses-az/aumt/"),
    ("Biology",                     "BIOL",  "/courses-az/biol/"),
    ("Biomedical Equipment",        "BIOM",  "/courses-az/biom/"),
    ("Biotechnology",               "BITC",  "/courses-az/bitc/"),
    ("Business",                    "BUSG",  "/courses-az/busg/"),
    ("Business",                    "BUSI",  "/courses-az/busi/"),
    ("Business Management",         "BMGT",  "/courses-az/bmgt/"),
    ("Business Management",         "HRPO",  "/courses-az/hrpo/"),
    ("Business Management",         "MRKG",  "/courses-az/mrkg/"),
    ("Business Office Technology",  "POFI",  "/courses-az/pofi/"),
    ("Business Office Technology",  "POFM",  "/courses-az/pofm/"),
    ("Business Office Technology",  "POFT",  "/courses-az/poft/"),
    ("Business Technology",         "BCIS",  "/courses-az/bcis/"),
    ("Chemistry",                   "CHEM",  "/courses-az/chem/"),
    ("Child Development",           "CDEC",  "/courses-az/cdec/"),
    ("Child Development",           "TECA",  "/courses-az/teca/"),
    ("Chinese",                     "CHIN",  "/courses-az/chin/"),
    ("College Preparatory",         "GUST",  "/courses-az/gust/"),
    ("College Preparatory",         "INRW",  "/courses-az/inrw/"),
    ("Commercial Photography",      "PHTC",  "/courses-az/phtc/"),
    ("Communications",              "COMM",  "/courses-az/comm/"),
    ("Computer Info Technology",    "CSIS",  "/courses-az/csis/"),
    ("Computer Info Technology",    "CYBR",  "/courses-az/cybr/"),
    ("Computer Info Technology",    "GAME",  "/courses-az/game/"),
    ("Computer Info Technology",    "INEW",  "/courses-az/inew/"),
    ("Computer Info Technology",    "ITAI",  "/courses-az/itai/"),
    ("Computer Info Technology",    "ITCC",  "/courses-az/itcc/"),
    ("Computer Info Technology",    "ITCS",  "/courses-az/itcs/"),
    ("Computer Info Technology",    "ITNW",  "/courses-az/itnw/"),
    ("Computer Info Technology",    "ITSC",  "/courses-az/itsc/"),
    ("Computer Info Technology",    "ITSE",  "/courses-az/itse/"),
    ("Computer Info Technology",    "ITSW",  "/courses-az/itsw/"),
    ("Computer Info Technology",    "ITSY",  "/courses-az/itsy/"),
    ("Computer Info / Art",         "IMED",  "/courses-az/imed/"),
    ("Computer Science",            "COSC",  "/courses-az/cosc/"),
    ("Construction Technology",     "CNBT",  "/courses-az/cnbt/"),
    ("Cosmetology",                 "CSME",  "/courses-az/csme/"),
    ("Cosmetology / Barber",        "BARB",  "/courses-az/barb/"),
    ("Criminal Justice",            "CJCR",  "/courses-az/cjcr/"),
    ("Criminal Justice",            "CJLE",  "/courses-az/cjle/"),
    ("Criminal Justice",            "CJSA",  "/courses-az/cjsa/"),
    ("Criminal Justice",            "CRIJ",  "/courses-az/crij/"),
    ("Culinary Arts",               "CHEF",  "/courses-az/chef/"),
    ("Culinary Arts",               "IFWA",  "/courses-az/ifwa/"),
    ("Culinary Arts",               "PSTR",  "/courses-az/pstr/"),
    ("Culinary Arts",               "RSTO",  "/courses-az/rsto/"),
    ("Dance",                       "DANC",  "/courses-az/danc/"),
    ("Dance",                       "DNCE",  "/courses-az/dnce/"),
    ("Diesel Technology",           "DEMR",  "/courses-az/demr/"),
    ("Diesel Technology",           "ELMT",  "/courses-az/elmt/"),
    ("Drama",                       "DRAM",  "/courses-az/dram/"),
    ("Economics",                   "ECON",  "/courses-az/econ/"),
    ("Education",                   "EDEC",  "/courses-az/edec/"),
    ("Education",                   "EDEL",  "/courses-az/edel/"),
    ("Education",                   "EDLL",  "/courses-az/edll/"),
    ("Education",                   "EDTP",  "/courses-az/edtp/"),
    ("Education",                   "EDUC",  "/courses-az/educ/"),
    ("Electrical Technology",       "CETT",  "/courses-az/cett/"),
    ("Electrical Technology",       "EECT",  "/courses-az/eect/"),
    ("Electrical Technology",       "ELPT",  "/courses-az/elpt/"),
    ("Electrical Technology",       "ENER",  "/courses-az/ener/"),
    ("Electrical Technology",       "RBPT",  "/courses-az/rbpt/"),
    ("Electronics Technology",      "RBTC",  "/courses-az/rbtc/"),
    ("Emergency Medical Services",  "EMSP",  "/courses-az/emsp/"),
    ("Engineering Design Graphics", "ARCE",  "/courses-az/arce/"),
    ("Engineering Design Graphics", "DFTG",  "/courses-az/dftg/"),
    ("Engineering",                 "ENGR",  "/courses-az/engr/"),
    ("Engineering Technology",      "ENTC",  "/courses-az/entc/"),
    ("English",                     "ENGL",  "/courses-az/engl/"),
    ("English for Speakers of Other Languages", "ESOL", "/courses-az/esol/"),
    ("English / Technical Writing", "ETWR",  "/courses-az/etwr/"),
    ("Entrepreneurial",             "ENTR",  "/courses-az/entr/"),
    ("Environmental Technology",    "EPCT",  "/courses-az/epct/"),
    ("Eye Care Technology",         "OPTS",  "/courses-az/opts/"),
    ("Fire Protection Technology",  "FIRS",  "/courses-az/firs/"),
    ("Fire Protection Technology",  "FIRT",  "/courses-az/firt/"),
    ("French",                      "FREN",  "/courses-az/fren/"),
    ("Geography",                   "GEOG",  "/courses-az/geog/"),
    ("Geology",                     "GEOL",  "/courses-az/geol/"),
    ("German",                      "GERM",  "/courses-az/germ/"),
    ("Global Logistics",            "IBUS",  "/courses-az/ibus/"),
    ("Global Logistics",            "LMGT",  "/courses-az/lmgt/"),
    ("Government",                  "GOVT",  "/courses-az/govt/"),
    ("Health Information Technology","HITT", "/courses-az/hitt/"),
    ("Health Professions",          "HPRS",  "/courses-az/hprs/"),
    ("History",                     "HIST",  "/courses-az/hist/"),
    ("Hospitality Administration",  "HAMG",  "/courses-az/hamg/"),
    ("Humanities",                  "HUMA",  "/courses-az/huma/"),
    ("Instrumentation",             "INCR",  "/courses-az/incr/"),
    ("Instrumentation Technology",  "INTC",  "/courses-az/intc/"),
    ("Interior Design",             "INDS",  "/courses-az/inds/"),
    ("Long Term Care",              "LTCA",  "/courses-az/ltca/"),
    ("Mammography",                 "MAMT",  "/courses-az/mamt/"),
    ("Manufacturing",               "MFGT",  "/courses-az/mfgt/"),
    ("Maritime Administration",     "MARA",  "/courses-az/mara/"),
    ("Maritime Transportation",     "NAUT",  "/courses-az/naut/"),
    ("Massage Therapy",             "MSSG",  "/courses-az/mssg/"),
    ("Mathematics",                 "MATH",  "/courses-az/math/"),
    ("Medical Assisting",           "MDCA",  "/courses-az/mdca/"),
    ("Medical Imaging",             "CTMT",  "/courses-az/ctmt/"),
    ("Medical Imaging",             "DMSO",  "/courses-az/dmso/"),
    ("Medical Imaging",             "MRIT",  "/courses-az/mrit/"),
    ("Medical Imaging",             "RADR",  "/courses-az/radr/"),
    ("Medical Laboratory Technology","MLAB", "/courses-az/mlab/"),
    ("Mental Health Services",      "DAAC",  "/courses-az/daac/"),
    ("Mental Health Services",      "PMHS",  "/courses-az/pmhs/"),
    ("Mental Health Services",      "PSYT",  "/courses-az/psyt/"),
    ("Mental Health Services",      "SCWK",  "/courses-az/scwk/"),
    ("Music",                       "MUAP",  "/courses-az/muap/"),
    ("Music",                       "MUEN",  "/courses-az/muen/"),
    ("Music",                       "MUSI",  "/courses-az/musi/"),
    ("Nondestructive Testing",      "METL",  "/courses-az/metl/"),
    ("Nondestructive Testing",      "NDTE",  "/courses-az/ndte/"),
    ("Nondestructive Testing",      "QCTC",  "/courses-az/qctc/"),
    ("Nursing / BSN",               "NURS",  "/courses-az/nurs/"),
    ("Nursing / RN",                "RNSG",  "/courses-az/rnsg/"),
    ("Nursing / Vocational",        "VNSG",  "/courses-az/vnsg/"),
    ("Occupational Health & Safety","OSHT",  "/courses-az/osht/"),
    ("Occupational Therapy",        "OTHA",  "/courses-az/otha/"),
    ("Paralegal",                   "LGLA",  "/courses-az/lgla/"),
    ("Pharmacy Technician",         "PHRA",  "/courses-az/phra/"),
    ("Philosophy",                  "PHIL",  "/courses-az/phil/"),
    ("Phlebotomy",                  "PLAB",  "/courses-az/plab/"),
    ("Physical Education",          "PHED",  "/courses-az/phed/"),
    ("Physical Therapist Assistant","PTHA",  "/courses-az/ptha/"),
    ("Physics",                     "PHYS",  "/courses-az/phys/"),
    ("Plumber / Pipefitter",        "PFPB",  "/courses-az/pfpb/"),
    ("Process Technology",          "CTEC",  "/courses-az/ctec/"),
    ("Process Technology",          "PTAC",  "/courses-az/ptac/"),
    ("Process Technology",          "PTRT",  "/courses-az/ptrt/"),
    ("Psychology",                  "PSYC",  "/courses-az/psyc/"),
    ("Reading",                     "READ",  "/courses-az/read/"),
    ("Real Estate",                 "RELE",  "/courses-az/rele/"),
    ("Respiratory Care",            "RSPT",  "/courses-az/rspt/"),
    ("Sociology",                   "SOCI",  "/courses-az/soci/"),
    ("Spanish",                     "SPAN",  "/courses-az/span/"),
    ("Speech",                      "SPCH",  "/courses-az/spch/"),
    ("Surgical Technology",         "SRGT",  "/courses-az/srgt/"),
    ("Welding",                     "WLDG",  "/courses-az/wldg/"),
    ("Workplace Organization",      "INMT",  "/courses-az/inmt/"),
]

# ── Course code pattern ───────────────────────────────────────────────────────

COURSE_CODE_RE = re.compile(r'^([A-Z]{2,5})\s+(\d{4}[A-Z]?)\b')


def fetch(url: str, retries: int = 3) -> BeautifulSoup | None:
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=15,
                             headers={"User-Agent": "SJC-demo-scraper/1.0 (educational)"})
            r.raise_for_status()
            return BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  ✗  FAILED {url}: {e}", file=sys.stderr)
                return None


def parse_subject_page(soup: BeautifulSoup, prefix: str) -> list[dict]:
    """
    Extract course records from a subject page using semantic HTML classes.

    Structure per course:
      div.courseblock
        p.courseblocktitle
          span.detail-code      → course code
          span.detail-title     → course title
          span.detail-hours     → "3 Credits"
          span.detail-lec_lab_hours → "(3 Lec, 1 Lab)"
        div.courseblockextra    → description paragraph
        div.section > div.section__content  → prereqs / course type / etc.
    """
    courses = []

    for block in soup.find_all("div", class_="courseblock"):
        def _txt(cls):
            el = block.find(class_=cls)
            return el.get_text(strip=True) if el else ""

        code    = _txt("detail-code")
        title   = _txt("detail-title")
        credits = _txt("detail-hours")
        hours   = _txt("detail-lec_lab_hours").strip("() ")

        desc_el = block.find("div", class_="courseblockextra")
        description = desc_el.get_text(strip=True) if desc_el else ""

        prereqs     = ""
        coreqs      = ""
        course_type = ""

        for sec in block.find_all("div", class_="section__content"):
            t = sec.get_text(strip=True)
            tl = t.lower()
            if tl.startswith("prerequisite"):
                prereqs = re.sub(r'^[Pp]rerequisite\(?s?\)?:\s*', '', t).strip()
            elif "co-requisite" in tl or "corequisite" in tl:
                coreqs = re.sub(r'^[Cc]o-?[Rr]equisite\(?s?\)?:\s*', '', t).strip()
            elif tl.startswith("course type"):
                course_type = re.sub(r'^[Cc]ourse [Tt]ype:\s*', '', t).strip()

        if code:
            courses.append({
                "code":        code,
                "title":       title,
                "credits":     credits,
                "hours":       hours,
                "description": description,
                "prereqs":     prereqs,
                "coreqs":      coreqs,
                "type":        course_type,
            })

    return courses


def course_to_md(c: dict) -> str:
    lines = []
    header = f"**{c['code']}**"
    if c["title"]:
        header += f" — {c['title']}"
    parts = []
    if c["credits"]:
        parts.append(c["credits"])
    if c["hours"]:
        parts.append(c["hours"])
    if parts:
        header += f" | {', '.join(parts)}"
    lines.append(header)

    if c["description"]:
        lines.append(c["description"])
    if c["prereqs"]:
        lines.append(f"*Prerequisite(s): {c['prereqs']}*")
    if c["coreqs"]:
        lines.append(f"*Co-requisite(s): {c['coreqs']}*")
    if c["type"]:
        lines.append(f"*Course Type: {c['type']}*")
    return "\n".join(lines)


def main():
    print("San Jacinto College — Course Catalog Scraper")
    print("=" * 50)
    print(f"Subjects: {len(SUBJECTS)}  |  Output: {OUTPUT}\n")

    sections = []
    total_courses = 0

    seen_urls = set()
    for dept_name, prefix, path in SUBJECTS:
        url = BASE_URL + path
        if url in seen_urls:
            continue
        seen_urls.add(url)

        print(f"  {prefix:<6}  {dept_name}", end=" ... ", flush=True)
        soup = fetch(url)
        if soup is None:
            print("SKIPPED")
            continue

        courses = parse_subject_page(soup, prefix)
        total_courses += len(courses)
        print(f"{len(courses)} courses")

        if courses:
            section_lines = [f"## {dept_name} ({prefix})\n"]
            for c in courses:
                section_lines.append(course_to_md(c))
                section_lines.append("")   # blank line between courses
            sections.append("\n".join(section_lines))

        time.sleep(DELAY)

    # Build final document
    header = f"""# San Jacinto College Course Catalog
*2026-2027 Academic Year*
*Source: publications.sanjac.edu | Scraped for Snowflake Cortex Search demo*

This document contains course descriptions, prerequisites, credit hours, and course
type classifications for all {total_courses} credit courses offered at San Jacinto College.
Use this with Cortex Search to enable natural-language lookup of courses, prerequisites,
and program requirements.

---

"""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(header + "\n---\n\n".join(sections), encoding="utf-8")

    print(f"\nDone — {total_courses} courses written to {OUTPUT}")


if __name__ == "__main__":
    main()
