from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data" / "cleaned_jobs.csv"
OUT = BASE / "data" / "eda_outputs"
OUT.mkdir(exist_ok=True)

def load_data():
    return pd.read_csv(DATA)

def explode_skills(df):
    x = df[["job_title","skills"]].copy()
    x["skills"] = x["skills"].fillna("").str.split(";")
    x = x.explode("skills")
    x["skills"] = x["skills"].str.strip()
    return x[x["skills"] != ""]

def run_eda():
    df = load_data()
    skill_df = explode_skills(df)
    top = skill_df["skills"].value_counts().head(15)

    plt.figure(figsize=(10,6))
    sns.barplot(x=top.values, y=top.index)
    plt.title("Top In-Demand Skills")
    plt.xlabel("Job postings mentioning skill")
    plt.ylabel("Skill")
    plt.tight_layout()
    plt.savefig(OUT/"top_skills.png", dpi=160)
    plt.close()

    role_salary = df.groupby("job_title")["salary_lpa"].median().sort_values(ascending=False)
    plt.figure(figsize=(10,6))
    sns.barplot(x=role_salary.values, y=role_salary.index)
    plt.title("Median Salary by Role")
    plt.xlabel("Median salary (LPA)")
    plt.ylabel("Role")
    plt.tight_layout()
    plt.savefig(OUT/"salary_by_role.png", dpi=160)
    plt.close()

    print("EDA charts saved in data/eda_outputs/")

if __name__ == "__main__":
    run_eda()
