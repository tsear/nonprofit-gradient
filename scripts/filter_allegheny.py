import pandas as pd
from pathlib import Path

input_path = Path("data/raw/eo_pa.csv")
output_path = Path("data/processed/allegheny_nonprofits.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

print(f"📥 Loading IRS dataset from: {input_path.resolve()}")

try:
    df = pd.read_csv(input_path, dtype=str)
    print(f"✅ Loaded {len(df)} rows.")
except Exception as e:
    print(f"❌ ERROR: Failed to load CSV — {e}")
    exit(1)

print("🔧 Normalizing ZIPs and city names...")
df["CITY"] = df["CITY"].str.upper().str.strip()
df["STATE"] = df["STATE"].str.upper().str.strip()
df["ZIP"] = df["ZIP"].str[:5]

allegheny_cities = {
    "PITTSBURGH", "BRADDOCK", "DUQUESNE", "MCKEESPORT", "MONROEVILLE",
    "MUNHALL", "NORTH VERSAILLES", "SWISSVALE", "TARENTUM", "WILKINSBURG",
    "HOMESTEAD", "CLAIRTON", "PENN HILLS", "MOUNT OLIVER", "WEST MIFFLIN",
    "BALDWIN", "BELLEVUE", "BLOOMFIELD", "SHARPSBURG", "MILLVALE", "EDGEWOOD"
}

print("🔍 Filtering for Allegheny County orgs...")
mask = (
    (df["STATE"] == "PA") &
    (
        df["CITY"].isin(allegheny_cities) |
        df["ZIP"].str.startswith(("151", "152"))
    )
)
allegheny_df = df[mask]

print(f"✅ Found {len(allegheny_df)} Allegheny County nonprofits")

if len(allegheny_df) == 0:
    print("⚠️ WARNING: Filter returned no results. Double-check data format.")
else:
    allegheny_df.to_csv(output_path, index=False)
    print(f"💾 Saved to: {output_path.resolve()}")