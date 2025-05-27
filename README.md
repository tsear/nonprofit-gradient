# 🧠 Nonprofit Gradient — Smart Grant Intelligence Dashboard

**Built by Smart Grant Solutions**  
_A pragmatic system for surfacing high-priority nonprofit leads and visualizing the philanthropic landscape._

---

## 🚀 Project Overview

This project combines public IRS Form 990 data with machine learning-driven prioritization to help teams:
- Understand the nonprofit sector at scale
- Identify ideal prospects by revenue, sector, and mission alignment
- Visualize momentum, financial capacity, and organizational focus
- Export filtered, high-signal lead lists for outreach

What started as a data-cleaning experiment evolved into a purpose-built sales intelligence dashboard. It helps our internal teams (and now, others) find, rank, and connect with high-opportunity nonprofit organizations.

---

## 🎯 Goals

- **Collect + normalize** IRS 990 data for thousands of nonprofits
- **Score** organizations across multiple axes (e.g., revenue, volatility, program %)
- **Expose insights** through clean, interpretable visualizations
- **Filter and export** high-priority orgs by custom criteria
- **Enable anyone** to run the dashboard locally with minimal technical skill

---

## 🛠 Tools & Stack

- `Python 3.10+`
- `Pandas` for data manipulation
- `Plotly` for interactive charts
- `scikit-learn` for clustering + scaling
- `Streamlit` for dashboard front-end
- `Matplotlib` + `Seaborn` for exploratory visuals (now deprecated in favor of Plotly)
- Data source: IRS 990 filings + internal enrichment pipelines

---

## 📈 Dashboard Highlights

- ✅ Interactive filters: Sector, ZIP, revenue, momentum, etc.
- ✅ Export filtered orgs to CSV
- ✅ Pre-clustered organizations using KMeans
- ✅ Top 10 leaderboard based on priority + financial strength
- ✅ Sector/Flag breakdown visualizations (minimal but insightful)
---

## 🧰 How to Run This Yourself (Even If You're Not a Developer)

> **Prereqs:** Python 3.10+ installed  
> If you're on a Mac, we recommend installing Python via [Homebrew](https://brew.sh).

### 🔨 1. Clone this repo
```bash
git clone https://github.com/YOUR_USERNAME/nonprofit-gradient.git
cd nonprofit-gradient

### 🧪 2. Set up a virtual environment
```bash
python3 -m venv env
source env/bin/activate

### 📦 3. Install dependencies
```bash
pip install -r requirements.txt

### 🚦 4. Run the dashboard
```bash
streamlit run app/ui_dashboard.py

This will open the dashboard in your browser. You can apply filters, explore the data, and download your own lead lists.

👀 Results & Insights

We found that the most actionable nonprofit leads:
	•	Have high program-to-revenue ratios (indicating operational focus)
	•	Sit in underrepresented sectors with strong average scores
	•	Are financially capable (revenue > $10M) but not yet flagged internally
	•	Exist in regional clusters that warrant geographically-focused outreach

Over 25,000 organizations were analyzed. All scoring logic is transparent and reproducible.

👥 Authors & Contributors

Tyler Sear – Lead engineer, analyst, and author
Smart Grant Solutions – Infrastructure + internal use case
Contact: tylersear910@gmail.com | Dayna@smartgrantsolutions.com

🧼 Disclaimer

This tool leverages public IRS filings (Form 990) and internal scoring metrics. It is a research and prioritization tool, not a definitive indicator of organizational value or eligibility. Use it to surface strong leads, but always validate manually before engagement.
