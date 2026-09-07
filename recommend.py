from pathlib import Path
import json
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
ROLE_FILE = BASE / "data" / "role_skills.json"

def load_roles():
    return json.loads(ROLE_FILE.read_text())

def normalise(s):
    return str(s).strip().lower()

def score_role(user_skills, required_skills):
    user = {normalise(x) for x in user_skills}
    required = {normalise(x) for x in required_skills}
    matched = sorted(user & required)
    missing = sorted(required - user)
    score = round(100 * len(matched) / max(1, len(required)), 1)
    return score, matched, missing

def recommend(user_skills, top_n=5):
    roles = load_roles()
    results = []
    for role, required in roles.items():
        score, matched, missing = score_role(user_skills, required)
        results.append({
            "role": role,
            "match_score": score,
            "matched_skills": matched,
            "missing_skills": missing,
        })
    return sorted(results, key=lambda x: x["match_score"], reverse=True)[:top_n]
