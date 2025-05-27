import pandas as pd
import json
from pathlib import Path

# === File paths ===
input_file = Path("data/processed/allegheny_nonprofits.csv")
sector_map_file = Path("data/sector_map.json")
mapped_output = Path("data/processed/allegheny_mapped.csv")
summary_by_sector = Path("data/processed/summary_by_sector.csv")
summary_by_zip = Path("data/processed/summary_by_zip.csv")
top_orgs_output = Path("data/processed/top_orgs_by_revenue.csv")

# === Load data ===
df = pd.read_csv(input_file, dtype=str)
with open(sector_map_file, "r") as f:
    sector_map = json.load(f)

# === Clean and map NTEE sector ===
def get_sector(ntee_code):
    if not isinstance(ntee_code, str) or len(ntee_code.strip()) == 0:
        return "Unknown"
    prefix = ntee_code.strip().upper()[0]
    return sector_map.get(prefix, "Unknown")

df["NTEE_CD"] = df["NTEE_CD"].fillna("").astype(str)
df["SECTOR"] = df["NTEE_CD"].apply(get_sector)

# === Normalize numeric fields ===
df["INCOME_AMT"] = pd.to_numeric(df["INCOME_AMT"], errors="coerce")
df["ASSET_AMT"] = pd.to_numeric(df["ASSET_AMT"], errors="coerce")
df["REVENUE_AMT"] = pd.to_numeric(df["REVENUE_AMT"], errors="coerce")

# === Size bucket classification ===
def size_bucket(rev):
    if pd.isna(rev): return "Unknown"
    if rev < 50000: return "Micro"
    if rev < 250000: return "Small"
    if rev < 1000000: return "Medium"
    if rev < 10000000: return "Large"
    return "Major"

df["SIZE_BUCKET"] = df["INCOME_AMT"].apply(size_bucket)

# === Save mapped file ===
df.to_csv(mapped_output, index=False)
print(f"✅ Saved mapped org file to {mapped_output}")

# === Summary by sector ===
sector_summary = df.groupby("SECTOR").agg(
    org_count = ("EIN", "count"),
    total_revenue = ("INCOME_AMT", "sum"),
    avg_revenue = ("INCOME_AMT", "mean")
).round(2).reset_index()

size_counts = df.pivot_table(index="SECTOR", columns="SIZE_BUCKET", values="EIN", aggfunc="count", fill_value=0)
sector_summary = sector_summary.merge(size_counts, on="SECTOR", how="left")
sector_summary.to_csv(summary_by_sector, index=False)
print(f"📊 Saved summary by sector to {summary_by_sector}")

# === Summary by ZIP ===
zip_summary = df.groupby("ZIP").agg(
    org_count = ("EIN", "count"),
    total_revenue = ("INCOME_AMT", "sum"),
    avg_revenue = ("INCOME_AMT", "mean")
).round(2).reset_index()

# Exclude "Unknown" sector from dominant logic
dominant_sector = df[df["SECTOR"] != "Unknown"] \
    .groupby(["ZIP", "SECTOR"]).size().reset_index(name="count")

dominant = dominant_sector.sort_values("count", ascending=False).drop_duplicates("ZIP")
zip_summary = zip_summary.merge(dominant[["ZIP", "SECTOR"]], on="ZIP", how="left")
zip_summary.rename(columns={"SECTOR": "dominant_sector"}, inplace=True)
zip_summary.to_csv(summary_by_zip, index=False)
print(f"📌 Saved summary by ZIP to {summary_by_zip}")

# === Top orgs by revenue ===
top_orgs = df.sort_values("INCOME_AMT", ascending=False).head(100)
top_orgs[["EIN", "NAME", "SECTOR", "INCOME_AMT", "ASSET_AMT", "ZIP"]].to_csv(top_orgs_output, index=False)
print(f"🏆 Saved top orgs by revenue to {top_orgs_output}")