import re
from .recommend import recommend, load_roles

def answer(question, user_skills):
    q = question.lower().strip()
    recs = recommend(user_skills, top_n=5)

    if any(w in q for w in ["skill gap", "gap", "missing skill"]):
        best = recs[0]
        return (
            f"Your strongest current career match is {best['role']} at {best['match_score']}%. "
            f"The main skills to add for that role are: {', '.join(best['missing_skills']) or 'none — you already cover the listed skills'}."
        )

    if "recommend" in q or "career" in q or "role" in q:
        lines = [f"{r['role']}: {r['match_score']}% match" for r in recs]
        return "Based on the skills you entered, I recommend:\n" + "\n".join(lines)

    # Skill-specific question
    roles = load_roles()
    mentioned = [s for skills in roles.values() for s in skills if s.lower() in q]
    if mentioned:
        skill = mentioned[0]
        matching_roles = [role for role, skills in roles.items() if skill in skills]
        return f"{skill} appears in these target roles: {', '.join(matching_roles)}."

    return (
        "I can answer questions about your skill gap, recommended roles, missing skills, "
        "and where a skill is used. Try: 'What skills am I missing?' or 'Which career should I choose?'"
    )
