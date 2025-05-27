import pandas as pd
from pathlib import Path
import numpy as np

# === File paths ===
input_file = Path("data/processed/financial_timeseries.csv")
output_file = Path("data/processed/org_trajectories.csv")

# === Load & filter ===
df = pd.read_csv(input_file, dtype=str)
df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce")
df["REVENUE"] = pd.to_numeric(df["REVENUE"], errors="coerce")
df = df[df["YEAR"].between(2019, 2023)]

# === Pivot: One row per org, one column per year ===
pivot = df.pivot_table(index=["EIN", "ORG_NAME"], columns="YEAR", values="REVENUE")
pivot.columns = [f"REV_{int(c)}" for c in pivot.columns]
pivot.reset_index(inplace=True)

# === Helper: Calculate CAGR ===
def calc_cagr(row):
    start = row.get("REV_2019")
    end = row.get("REV_2023")
    if pd.isna(start) or pd.isna(end) or start <= 0:
        return np.nan
    return ((end / start) ** (1 / 4)) - 1  # 4 years

# === Apply metrics ===
pivot["CAGR"] = pivot.apply(calc_cagr, axis=1)
pivot["VOLATILITY"] = pivot[[f"REV_{y}" for y in range(2019, 2024)]].std(axis=1)

# Count how many years increased or decreased
def count_deltas(row):
    up = down = 0
    revs = [row.get(f"REV_{y}") for y in range(2019, 2024)]
    for a, b in zip(revs, revs[1:]):
        if pd.notna(a) and pd.notna(b):
            if b > a:
                up += 1
            elif b < a:
                down += 1
    return up, down

pivot["YEARS_UP"], pivot["YEARS_DOWN"] = zip(*pivot.apply(count_deltas, axis=1))

# Peak / trough year
def peak_year(row):
    revs = {y: row.get(f"REV_{y}") for y in range(2019, 2024)}
    revs = {y: v for y, v in revs.items() if pd.notna(v)}
    return max(revs, key=revs.get) if revs else np.nan

def trough_year(row):
    revs = {y: row.get(f"REV_{y}") for y in range(2019, 2024)}
    revs = {y: v for y, v in revs.items() if pd.notna(v)}
    return min(revs, key=revs.get) if revs else np.nan

pivot["PEAK_YEAR"] = pivot.apply(peak_year, axis=1)
pivot["TROUGH_YEAR"] = pivot.apply(trough_year, axis=1)

# Rebound rate: % change from trough to most recent
def rebound_rate(row):
    try:
        trough = row[f"REV_{int(row['TROUGH_YEAR'])}"]
        final = row.get("REV_2023")
        if pd.isna(trough) or pd.isna(final) or trough <= 0:
            return np.nan
        return ((final - trough) / trough) * 100
    except:
        return np.nan

pivot["REBOUND_RATE"] = pivot.apply(rebound_rate, axis=1)

# Final formatting
pivot["CAGR"] = (pivot["CAGR"] * 100).round(2)
pivot["VOLATILITY"] = pivot["VOLATILITY"].round(0)
pivot["REBOUND_RATE"] = pivot["REBOUND_RATE"].round(2)

# Save
pivot.to_csv(output_file, index=False)
print(f"✅ Saved 5-year org trajectories to {output_file}")
print(f"📈 Total orgs: {len(pivot)}")