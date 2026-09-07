import re
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "jobs_raw.csv"
OUT = BASE / "data" / "cleaned_jobs.csv"

def clean_skill_text(value):
    if pd.isna(value):
        return ""
    value = str(value).replace("|", ";").replace(",", ";")
    parts = [re.sub(r"\\s+", " ", p.strip()) for p in value.split(";")]
    parts = [p for p in parts if p]
    # remove duplicate skills while keeping order
    seen = set()
    cleaned = []
    for p in parts:
        key = p.lower()
        if key not in seen:
            seen.add(key)
            cleaned.append(p)
    return "; ".join(cleaned)

def main():
    df = pd.read_csv(RAW)
    df.columns = (
        df.columns.astype(str).str.strip().str.lower()
        .str.replace(r"[^a-z0-9_]+", "_", regex=True)
        .str.strip("_")
    )

    # Make the project resilient to common job-dataset column names.
    aliases = {
        "title": "job_title",
        "job_title": "job_title",
        "jobtitle": "job_title",
        "companyname": "company",
        "company_name": "company",
        "company": "company",
        "location": "location",
        "salary": "salary_inr",
        "salary_inr": "salary_inr",
        "tagsandskills": "skills",
        "skills_required": "skills",
        "skills": "skills",
    }
    for old, new in list(aliases.items()):
        if old in df.columns and new not in df.columns:
            df[new] = df[old]

    required = ["job_title","company","location","salary_inr","skills"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing columns: {missing}. Open jobs_raw.csv and update the aliases in clean_data.py."
        )

    df["job_title"] = df["job_title"].fillna("Unknown").astype(str).str.strip()
    df["company"] = df["company"].fillna("Unknown").astype(str).str.strip()
    df["location"] = df["location"].fillna("Unknown").astype(str).str.strip()
    df["skills"] = df["skills"].apply(clean_skill_text)
    df["salary_inr"] = pd.to_numeric(
        df["salary_inr"].astype(str).str.replace(r"[^0-9.]", "", regex=True),
        errors="coerce"
    )
    df = df.dropna(subset=["job_title","skills"]).copy()
    df = df.drop_duplicates()
    df["salary_lpa"] = df["salary_inr"] / 100000
    df.to_csv(OUT, index=False)
    print(f"Saved {len(df):,} rows to {OUT}")

if __name__ == "__main__":
    main()
