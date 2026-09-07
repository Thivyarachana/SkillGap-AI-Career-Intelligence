# 🎯 SkillGap AI — Career Intelligence Dashboard

A portfolio-ready data analytics project that turns job-market data into:
- cleaned data
- EDA and visualizations
- skill-demand analytics
- personal skill-gap scoring
- career recommendations
- conversational career assistant
- Power BI executive dashboard
- Streamlit web application

## Quick start

### 1. Create a virtual environment
Windows:
`python -m venv .venv`
`.venv\Scripts\activate`

macOS/Linux:
`python3 -m venv .venv`
`source .venv/bin/activate`

### 2. Install packages
`pip install -r requirements.txt`

### 3. Clean the sample data
`python src/clean_data.py`

### 4. Generate EDA charts
`python src/analysis.py`

### 5. Start the web app
`streamlit run app.py`

The browser should open automatically.

## Replace the demo data with real data

Download a real job-market CSV and replace `data/jobs_raw.csv`.
Then run:
`python src/clean_data.py`

If your column names are different, update the `aliases` dictionary in
`src/clean_data.py`.

## GitHub

Create a public repository, add the project files, commit, and push.
Do NOT commit API keys or `.env` files.

## Important
The included CSV is synthetic demo data so the project runs immediately.
For your final portfolio version, replace it with a documented real dataset
and mention the source and license in your README.
