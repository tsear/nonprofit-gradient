import pandas as pd
import plotly.express as px
import streamlit as st

# === Load data ===
df = pd.read_csv("data/processed/org_master_profiles_scored.csv")
df = df[df["REVENUE"] <= 2_000_000_000]  # Drop extreme outliers

# === Streamlit Setup ===
st.set_page_config(page_title="Target Dashboard", layout="wide")
st.title("📊 Smart Grant Solutions — Sales Intelligence Dashboard")

# === Sidebar Filters ===
st.sidebar.header("Filter Orgs")

def fallback_multiselect(label, options):
    selection = st.sidebar.multiselect(label, sorted(options))
    return selection if selection else list(options)

revenue_range = st.sidebar.slider("Revenue", int(df["REVENUE"].min()), int(df["REVENUE"].max()),
                                  (int(df["REVENUE"].min()), int(df["REVENUE"].max())))
priority_range = st.sidebar.slider("Priority Score", int(df["PRIORITY_SCORE"].min()),
                                   int(df["PRIORITY_SCORE"].max()),
                                   (int(df["PRIORITY_SCORE"].min()), int(df["PRIORITY_SCORE"].max())))
sectors = fallback_multiselect("Sector", df["SECTOR"].dropna().unique())
flags = fallback_multiselect("Target Flag", df["TARGET_FLAG"].dropna().unique())
momentums = fallback_multiselect("Momentum Class", df["MOMENTUM_CLASS"].dropna().unique())
zip_prefix = st.sidebar.text_input("ZIP (prefix)", "")

# === Apply Filters ===
filtered_df = df[
    (df["REVENUE"].between(*revenue_range)) &
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
st.dataframe(filtered_df.sort_values(by="PRIORITY_SCORE", ascending=False).reset_index(drop=True), use_container_width=True)

# === Chart 1: Target Flag by Sector ===
st.subheader("📊 Target Flag Distribution by Sector")
st.markdown("This shows how different org types (target flags) are distributed across sectors.")
flag_sector = filtered_df.groupby(["SECTOR", "TARGET_FLAG"]).size().reset_index(name="count")
fig1 = px.bar(flag_sector, x="SECTOR", y="count", color="TARGET_FLAG", barmode="group",
              title="Target Flag Count by Sector")
st.plotly_chart(fig1, use_container_width=True)

# === Chart 2: Momentum Watchlist Breakdown ===
st.subheader("🔥 Momentum Watchlist by Sector")
st.markdown("Shows which sectors have high average momentum among orgs not currently flagged high priority.")
watchlist_df = filtered_df[filtered_df["TARGET_FLAG"].str.lower() != "high_priority"]
momentum_avg = watchlist_df.groupby("SECTOR")["MOMENTUM_SCORE"].mean().reset_index()
fig2 = px.bar(momentum_avg, x="SECTOR", y="MOMENTUM_SCORE", title="Avg Momentum Score (Watchlist Orgs)")
st.plotly_chart(fig2, use_container_width=True)