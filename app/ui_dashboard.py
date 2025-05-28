import pandas as pd
import plotly.express as px
import streamlit as st

# === Load primary data ===
df = pd.read_csv("data/processed/org_master_profiles_scored.csv")
momentum_df = pd.read_csv("data/processed/momentum_classification.csv")

# Check for negative revenue
has_negative_revenue = (df["REVENUE"] < 0).any()

# === Streamlit Setup ===
st.set_page_config(page_title="Target Dashboard", layout="wide")
st.title("📊 Smart Grant Solutions — Sales Intelligence Dashboard")

if has_negative_revenue:
    st.warning(
        "⚠️ Some organizations report negative revenue. While rare, this may reflect accounting nuances or reporting errors. "
        "These values are retained in the dataset, but the default view excludes them."
    )

# === Sidebar Filters ===
st.sidebar.header("Filter Orgs")

def fallback_multiselect(label, options):
    selection = st.sidebar.multiselect(label, sorted(options))
    return selection if selection else list(options)

# Revenue filter range
filtered_revenue_min = 0
filtered_revenue_max = 200_000_000

st.sidebar.markdown(
    "⚠️ For visualization clarity, orgs with revenue above **$200M** are excluded from the default slider range. "
    "There are 19 such orgs, and they are displayed separately below."
)

revenue_range = st.sidebar.slider(
    "Revenue (USD)",
    min_value=filtered_revenue_min,
    max_value=filtered_revenue_max,
    value=(filtered_revenue_min, filtered_revenue_max),
    step=1_000_000
)

priority_range = st.sidebar.slider(
    "Priority Score",
    min_value=int(df["PRIORITY_SCORE"].min()),
    max_value=int(df["PRIORITY_SCORE"].max()),
    value=(int(df["PRIORITY_SCORE"].min()), int(df["PRIORITY_SCORE"].max()))
)

sectors = fallback_multiselect("Sector", df["SECTOR"].dropna().unique())
flags = fallback_multiselect("Target Flag", df["TARGET_FLAG"].dropna().unique())
momentums = fallback_multiselect("Momentum Class", df["MOMENTUM_CLASS"].dropna().unique())
zip_prefix = st.sidebar.text_input("ZIP (prefix)", "")

# === Apply Filters ===
filtered_df = df[
    (df["REVENUE"] >= revenue_range[0]) &
    (df["REVENUE"] <= revenue_range[1]) &
    (df["PRIORITY_SCORE"].between(*priority_range)) &
    (df["SECTOR"].isin(sectors)) &
    (df["TARGET_FLAG"].isin(flags)) &
    (df["MOMENTUM_CLASS"].isin(momentums))
]

if zip_prefix:
    filtered_df = filtered_df[filtered_df["ZIP"].astype(str).str.startswith(zip_prefix)]

st.markdown(f"**{len(filtered_df):,} organizations match the filters.**")

# === Data Table (centerpiece) ===
st.subheader("📋 Explore the Filtered Organizations")
st.dataframe(
    filtered_df.sort_values(by="PRIORITY_SCORE", ascending=False).reset_index(drop=True),
    use_container_width=True
)

# === Chart 1: Target Flag by Sector (split Unknown) ===
st.subheader("📊 Target Flag Distribution by Sector")
st.markdown("This shows how different org types (target flags) are distributed across sectors. 'Unknown' is shown separately below.")

chart_df = filtered_df[filtered_df["REVENUE"] <= filtered_revenue_max]
flag_sector = chart_df.groupby(["SECTOR", "TARGET_FLAG"]).size().reset_index(name="count")

known_flag_sector = flag_sector[flag_sector["SECTOR"] != "Unknown"]
unknown_flag_sector = flag_sector[flag_sector["SECTOR"] == "Unknown"]

fig1 = px.bar(
    known_flag_sector,
    x="SECTOR",
    y="count",
    color="TARGET_FLAG",
    barmode="group",
    title="Target Flag Count by Sector (Excludes 'Unknown')"
)
fig1.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig1, use_container_width=True)

if not unknown_flag_sector.empty:
    st.subheader("🕵️ 'Unknown' Sector Overview")
    st.markdown("These orgs couldn’t be categorized into a clear sector.")
    fig_unknown = px.bar(
        unknown_flag_sector,
        x="SECTOR",
        y="count",
        color="TARGET_FLAG",
        barmode="group",
        title="Target Flag Count — Unknown Sector Only"
    )
    st.plotly_chart(fig_unknown, use_container_width=True)

# === Chart 2: Momentum Watchlist Breakdown ===
st.subheader("🔥 Momentum Watchlist by Sector & Class")
st.markdown("Average momentum scores grouped by sector and classification. Chart scaled to highlight meaningful signal only (−0.5 to 1.5).")

# Merge EIN → SECTOR
merged = pd.merge(momentum_df, df[["EIN", "SECTOR"]], on="EIN", how="left")
merged = merged[merged["SECTOR"].notna() & (merged["SECTOR"] != "Unknown")]

# Clip downward momentum more tightly (bottomed at −0.5)
merged["MOMENTUM_SCORE_CLIPPED"] = merged["MOMENTUM_SCORE"].clip(lower=-0.5, upper=1.5)

grouped = merged.groupby(["SECTOR", "MOMENTUM_CLASS"])["MOMENTUM_SCORE_CLIPPED"].mean().reset_index()

fig2 = px.bar(
    grouped,
    x="SECTOR",
    y="MOMENTUM_SCORE_CLIPPED",
    color="MOMENTUM_CLASS",
    barmode="group",
    title="Avg Momentum Score by Sector & Class (Scale: -0.5 to 1.5)"
)
fig2.update_layout(
    xaxis_tickangle=45,
    yaxis_range=[-0.5, 1.5],
    margin=dict(t=40, b=60),
)
st.plotly_chart(fig2, use_container_width=True)

# === Excluded High-Revenue Orgs ===
st.subheader("🚨 Excluded Orgs Over $200M Revenue")
excluded_df = df[df["REVENUE"] > filtered_revenue_max][[
    "ORG_NAME", "REVENUE", "PRIORITY_SCORE", "SECTOR", "TARGET_FLAG", "MOMENTUM_CLASS"
]]
st.markdown(f"**{len(excluded_df):,} organizations have revenue over $200M.**")
st.dataframe(excluded_df.reset_index(drop=True), use_container_width=True)