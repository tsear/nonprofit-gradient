import pandas as pd
from pathlib import Path

# === File paths ===
mapped_path = Path("data/processed/allegheny_mapped.csv")
momentum_path = Path("data/processed/momentum_classification.csv")
timeseries_path = Path("data/processed/financial_timeseries.csv")
output_combined = Path("data/processed/org_master_profiles.csv")
output_scoring = Path("data/processed/target_cohort_scores.csv")

# === Load data ===
mapped = pd.read_csv(mapped_path, dtype=str)
momentum = pd.read_csv(momentum_path, dtype=str)
timeseries = pd.read_csv(timeseries_path, dtype=str)

# Ensure numerics
momentum["AVG_RECENT_REVENUE"] = pd.to_numeric(momentum["AVG_RECENT_REVENUE"], errors="coerce")

timeseries["YEAR"] = pd.to_numeric(timeseries["YEAR"], errors="coerce")
timeseries["REVENUE"] = pd.to_numeric(timeseries["REVENUE"], errors="coerce")
timeseries["PROGRAM_PCT"] = pd.to_numeric(timeseries["PROGRAM_PCT"], errors="coerce")

# Use latest year per EIN
latest_year = timeseries.groupby("EIN")["YEAR"].max().reset_index()
latest_data = timeseries.merge(latest_year, on=["EIN", "YEAR"], how="inner")

# Keep only EIN + REVENUE + PROGRAM_PCT
if "PROGRAM_PCT" not in latest_data.columns:
    latest_data["PROGRAM_PCT"] = None
latest_data = latest_data[["EIN", "REVENUE", "PROGRAM_PCT"]]

# === Merge everything ===
df = mapped.merge(momentum, on="EIN", how="inner")
df = df.merge(latest_data, on="EIN", how="left")

# === Flag hollow orgs ===
def flag_hollow(row):
    try:
        rev = float(row["REVENUE"]) if row["REVENUE"] not in [None, "", "nan"] else 0
        pct = float(row["PROGRAM_PCT"]) if row["PROGRAM_PCT"] not in [None, "", "nan"] else 0
        return rev > 50000 and pct < 20
    except:
        return False

df["IS_HOLLOW"] = df.apply(flag_hollow, axis=1)

# === Flag turbulent momentum ===
df["IS_TURBULENT"] = df["MOMENTUM_CLASS"].str.lower().str.contains("turbulent")

# === Save merged profile ===
df.to_csv(output_combined, index=False)
print(f"✅ Full org profile saved to {output_combined}")

# === Grouped summary matrix ===
summary = df.groupby(["SECTOR", "SIZE_BUCKET", "MOMENTUM_CLASS"]).agg(
    ORG_COUNT=("EIN", "count"),
    AVG_REVENUE=("REVENUE", "mean"),
    AVG_PROGRAM_PCT=("PROGRAM_PCT", "mean"),
    PCT_HOLLOW=("IS_HOLLOW", "mean"),
    PCT_TURBULENT=("IS_TURBULENT", "mean")
).reset_index()

summary["AVG_REVENUE"] = summary["AVG_REVENUE"].round(0).astype("Int64")
summary["AVG_PROGRAM_PCT"] = summary["AVG_PROGRAM_PCT"].round(1)
summary["PCT_HOLLOW"] = (summary["PCT_HOLLOW"] * 100).round(1)
summary["PCT_TURBULENT"] = (summary["PCT_TURBULENT"] * 100).round(1)

summary.to_csv(output_scoring, index=False)
print(f"📊 Target cohort scoring grid saved to {output_scoring}")