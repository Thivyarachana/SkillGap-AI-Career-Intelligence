import sys
from pathlib import Path
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from src.recommend import recommend, load_roles
from src.chatbot import answer

st.set_page_config(
    page_title="SkillGap AI | Career Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    '''
    <style>
    .main {background: #0b1020;}
    [data-testid="stSidebar"] {background: #111827;}
    .hero {
        padding: 28px; border-radius: 20px; margin-bottom: 18px;
        background: linear-gradient(135deg,#111827,#1e293b);
        border: 1px solid #334155;
    }
    .hero h1 {font-size: 42px; margin-bottom: 4px;}
    .hero p {color:#cbd5e1; font-size:17px;}
    .card {
        padding: 18px; border-radius: 16px; background:#111827;
        border:1px solid #334155; margin-bottom:12px;
    }
    .small {color:#94a3b8;}
    </style>
    ''',
    unsafe_allow_html=True,
)

@st.cache_data
def load_jobs():
    return pd.read_csv(BASE/"data/cleaned_jobs.csv")

df = load_jobs()
all_skills = sorted({
    s.strip() for cell in df["skills"].dropna()
    for s in str(cell).split(";") if s.strip()
})

st.sidebar.title("🎯 SkillGap AI")
st.sidebar.caption("Career Intelligence Dashboard")
user_name = st.sidebar.text_input("Your name", "Student")
selected_skills = st.sidebar.multiselect(
    "Your current skills",
    all_skills,
    default=[s for s in ["Python","SQL","Power BI"] if s in all_skills]
)
target_role = st.sidebar.selectbox("Target role", ["All roles"] + list(load_roles().keys()))
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Overview","🧩 Skill Gap","🚀 Career Recommendations","📊 Market Analytics","🤖 AI Career Assistant"]
)

st.markdown(
    f'''<div class="hero">
    <h1>SkillGap <span style="color:#60a5fa">AI</span></h1>
    <p>Turn your current skills into a clear career plan using job-market analytics.</p>
    <p class="small">Welcome, {user_name}. Your dashboard is personalized from the skills you selected.</p>
    </div>''',
    unsafe_allow_html=True,
)

if page == "🏠 Overview":
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Job postings", f"{len(df):,}")
    c2.metric("Companies", f"{df['company'].nunique():,}")
    c3.metric("Roles", f"{df['job_title'].nunique():,}")
    c4.metric("Your skills", f"{len(selected_skills)}")

    # --------------------------------------------------
    # PERSONALIZED SKILL SUMMARY
    # --------------------------------------------------
    st.markdown("### 👤 Your Current Skill Profile")

    if selected_skills:
        skill_columns = st.columns(min(len(selected_skills), 4))

        for i, skill in enumerate(selected_skills):
            with skill_columns[i % len(skill_columns)]:
                st.success(f"✅ {skill}")
    else:
        st.info("Select your current skills from the sidebar to personalize your dashboard.")

    st.subheader("What this project does")
    st.write(
        "It cleans job-market data, explores demand, compares your skills with role requirements, "
        "recommends careers, and gives you a conversational career assistant."
    )

elif page == "🧩 Skill Gap":
    st.subheader("Your Skill Gap")

    # --------------------------------------------------
    # TARGET ROLE ANALYSIS
    # --------------------------------------------------
    if target_role != "All roles":
        role_recommendations = recommend(selected_skills, top_n=10)
        matching_role = next(
            (r for r in role_recommendations if r["role"] == target_role),
            None
        )

        if matching_role:
            best = matching_role
        else:
            best = role_recommendations[0]
    else:
        recs = recommend(selected_skills, top_n=1)
        best = recs[0]

    st.info(f"🎯 Analyzing your skills for: **{best['role']}**")

    # --------------------------------------------------
    # SKILL GAP BREAKDOWN
    # --------------------------------------------------
    matched_count = len(best["matched_skills"])
    missing_count = len(best["missing_skills"])
    total_skills = matched_count + missing_count

    if total_skills > 0:
        gap_data = pd.DataFrame({
            "Category": ["Matched Skills", "Missing Skills"],
            "Count": [matched_count, missing_count]
        })

        st.markdown("### 📊 Skill Gap Breakdown")

        fig, ax = plt.subplots(figsize=(6, 6))

        ax.pie(
            gap_data["Count"],
            labels=gap_data["Category"],
            autopct="%1.1f%%",
            startangle=90
        )

        ax.set_title(f"Your Skill Readiness for {best['role']}")

        st.pyplot(fig, clear_figure=True)
    st.metric(f"Best current match: {best['role']}", f"{best['match_score']}%")

    # --------------------------------------------------
    # CAREER READINESS SUMMARY
    # --------------------------------------------------
    score = best["match_score"]

    st.markdown("### 🎯 Career Readiness")

    if score >= 75:
        st.success(
            f"🟢 Strong Career Readiness — You have a strong skill foundation "
            f"for **{best['role']}**."
        )
    elif score >= 50:
        st.warning(
            f"🟡 Moderate Career Readiness — You have a good foundation, "
            f"but should strengthen some important skills for **{best['role']}**."
        )
    else:
        st.error(
            f"🔴 Early Career Readiness — Focus on the recommended skills "
            f"to become more job-ready for **{best['role']}**."
        )

    col1,col2 = st.columns(2)
    with col1:
        st.markdown("### ✅ Skills you already have")
        st.write(", ".join(best["matched_skills"]) or "No matching skills yet.")
    with col2:
        st.markdown("### 🔧 Skills to learn next")

        # --------------------------------------------------
        # PERSONALIZED CAREER ROADMAP
        # --------------------------------------------------
        st.markdown("### 🗺️ Personalized Career Roadmap")

        if best["missing_skills"]:
            st.write(
                f"Follow these steps to become more job-ready for **{best['role']}**:"
            )

            for i, skill in enumerate(best["missing_skills"], start=1):
                st.markdown(
                    f"**Step {i}:** 📚 Learn and practice **{skill}**"
                )

            st.success(
                "💡 Tip: Build a small project after learning the key skills "
                "to demonstrate your ability to recruiters."
            )
        else:
            st.success(
                f"🎉 You already have the key skills identified for {best['role']}!"
            )

        for skill in best["missing_skills"]:
            st.write(f"• {skill}")

    st.markdown("### Skill-gap progress")
    progress = best["match_score"] / 100
    st.progress(progress)

    # --------------------------------------------------
    # RECOMMENDED LEARNING ROADMAP
    # --------------------------------------------------
    st.markdown("### 🗺️ Recommended Learning Roadmap")

    if best["missing_skills"]:
        st.write(
            "Follow this roadmap to improve your readiness for "
            f"**{best['role']}**:"
        )

        for i, skill in enumerate(best["missing_skills"], start=1):
            st.markdown(f"**{i}. 📚 {skill}**")

            if i == 1:
                st.caption(
                    "⭐ Start with this skill first and build a strong foundation."
                )
            elif i <= 3:
                st.caption(
                    "🎯 High-priority skill for improving your career readiness."
                )
            else:
                st.caption(
                    "📈 Strengthen this skill after completing the fundamentals."
                )

            if i < len(best["missing_skills"]):
                st.write("⬇️")

    else:
        st.success(
            "🎉 You have no major skill gaps for this career. "
            "Focus on projects and interview preparation."
        )

    # --------------------------------------------------
    # TOP SKILLS TO LEARN
    # --------------------------------------------------
    if best["missing_skills"]:
        st.markdown("### 📚 Top Skills You Should Learn")

        learning_skills = best["missing_skills"][:7]

        skill_priority = pd.DataFrame({
            "Skill": learning_skills,
            "Priority": list(range(len(learning_skills), 0, -1))
        })

        fig, ax = plt.subplots(figsize=(9, 5))

        sns.barplot(
            data=skill_priority,
            x="Priority",
            y="Skill",
            ax=ax
        )

        ax.set_xlabel("Learning Priority")
        ax.set_ylabel("Skill")
        ax.set_title("Skills to Prioritize for Your Career")

        st.pyplot(fig, clear_figure=True)

elif page == "🚀 Career Recommendations":
    st.subheader("Career Recommendations")

    recommendations = recommend(selected_skills, top_n=5)

    # --------------------------------------------------
    # CAREER MATCH COMPARISON
    # --------------------------------------------------
    st.markdown("### 📊 Career Match Comparison")

    comparison_df = pd.DataFrame({
        "Career": [r["role"] for r in recommendations],
        "Match Score": [r["match_score"] for r in recommendations]
    })

    fig, ax = plt.subplots(figsize=(9, 5))

    sns.barplot(
        data=comparison_df,
        x="Match Score",
        y="Career",
        ax=ax
    )

    ax.set_xlabel("Skill Match (%)")
    ax.set_ylabel("")
    ax.set_title("How Well Your Skills Match Each Career")

    st.pyplot(fig, clear_figure=True)

    st.markdown("### 🎯 Detailed Recommendations")

    for r in recommendations:
        with st.container(border=True):
            st.markdown(f"### {r['role']}")
            st.progress(r["match_score"]/100, text=f"{r['match_score']}% skill match")
            st.write("**Matched:**", ", ".join(r["matched_skills"]) or "None")
            st.write("**Next skills:**", ", ".join(r["missing_skills"]) or "You're ready for the listed skills!")

            # --------------------------------------------------
            # SALARY INSIGHT
            # --------------------------------------------------
            role_salary = df[df["job_title"] == r["role"]]["salary_lpa"]

            if not role_salary.empty:
                median_salary = role_salary.median()
                st.metric(
                    "💰 Median Salary",
                    f"₹{median_salary:.1f} LPA"
                )

            # --------------------------------------------------
            # EXPERIENCE INSIGHT
            # --------------------------------------------------
            role_experience = df[df["job_title"] == r["role"]]["experience"]

            if not role_experience.empty:
                common_experience = role_experience.mode()

                if not common_experience.empty:
                    st.info(
                        f"💼 Most common experience level: **{common_experience.iloc[0]}**"
                    )

            # --------------------------------------------------
            # LOCATION INSIGHT
            # --------------------------------------------------
            role_locations = (
                df[df["job_title"] == r["role"]]["location"]
                .dropna()
                .value_counts()
                .head(5)
            )

            if not role_locations.empty:
                st.markdown("#### 📍 Top Job Locations")

                location_df = role_locations.reset_index()
                location_df.columns = ["Location", "Job Postings"]

                fig, ax = plt.subplots(figsize=(8, 4))

                sns.barplot(
                    data=location_df,
                    x="Job Postings",
                    y="Location",
                    ax=ax
                )

                ax.set_xlabel("Number of Job Postings")
                ax.set_ylabel("")
                ax.set_title(f"Top Locations for {r['role']}")

                st.pyplot(fig, clear_figure=True)

elif page == "📊 Market Analytics":
    st.subheader("Job Market Analytics")
    locs = ["All"] + sorted(df["location"].dropna().unique())
    chosen_loc = st.selectbox("Location filter", locs)
    view = df if chosen_loc=="All" else df[df["location"]==chosen_loc]

    left,right = st.columns(2)
    with left:
        st.markdown("#### Top demanded skills")
        skill_counts = (
            view["skills"].fillna("").str.split(";").explode().str.strip()
            .replace("", pd.NA).dropna().value_counts().head(12)
        )
        fig, ax = plt.subplots(figsize=(8,5))
        sns.barplot(x=skill_counts.values, y=skill_counts.index, ax=ax)
        ax.set_xlabel("Job postings")
        ax.set_ylabel("")
        st.pyplot(fig, clear_figure=True)
    with right:
        st.markdown("#### Median salary by role")
        salary = view.groupby("job_title")["salary_lpa"].median().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(8,5))
        sns.barplot(x=salary.values, y=salary.index, ax=ax)
        ax.set_xlabel("Median LPA")
        ax.set_ylabel("")
        st.pyplot(fig, clear_figure=True)

    st.dataframe(view.head(100), use_container_width=True)

elif page == "🤖 AI Career Assistant":
    st.subheader("AI Career Assistant")
    st.caption("Ask about your skill gap, career match, missing skills, or a specific technology.")
    if "chat" not in st.session_state:
        st.session_state.chat = []
    for role, msg in st.session_state.chat:
        with st.chat_message(role):
            st.write(msg)
    q = st.chat_input("Example: What skills am I missing for my best career?")
    if q:
        st.session_state.chat.append(("user", q))
        # --------------------------------------------------
        # PERSONALIZED AI CAREER ASSISTANT
        # --------------------------------------------------
        recommendations = recommend(selected_skills, top_n=1)

        if recommendations:
            best_chat_role = recommendations[0]

            context = f"""
User skills: {", ".join(selected_skills) if selected_skills else "No skills selected"}
Best career match: {best_chat_role["role"]}
Skill match score: {best_chat_role["match_score"]}%
Matched skills: {", ".join(best_chat_role["matched_skills"]) if best_chat_role["matched_skills"] else "None"}
Missing skills: {", ".join(best_chat_role["missing_skills"]) if best_chat_role["missing_skills"] else "None"}
"""

            response = answer(
                q,
                selected_skills
            )

            response = (
                response
                + "\n\n---\n"
                + "🎯 **Your Career Context**\n"
                + context
            )
        else:
            response = answer(q, selected_skills)

        st.session_state.chat.append(("assistant", response))
        st.rerun()


