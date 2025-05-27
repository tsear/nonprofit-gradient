import pandas as pd
import requests
import time
from pathlib import Path
import json

# Load EINs
df = pd.read_csv("data/processed/allegheny_mapped.csv", dtype=str)
eins = df["EIN"].dropna().unique().tolist()

output_dir = Path("data/financials_by_ein")
output_dir.mkdir(parents=True, exist_ok=True)

# API endpoint template
base_url = "https://projects.propublica.org/nonprofits/api/v2/organizations/{}.json"

for idx, ein in enumerate(eins):
    out_path = output_dir / f"{ein}.json"

    # Skip if already downloaded
    if out_path.exists():
        print(f"[{idx+1}/{len(eins)}] Skipping {ein} (already cached)")
        continue

    url = base_url.format(ein)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(out_path, "w") as f:
                json.dump(response.json(), f)
            print(f"[{idx+1}/{len(eins)}] ✅ Saved {ein}")
        else:
            print(f"[{idx+1}/{len(eins)}] ❌ Error {response.status_code} for {ein}")
    except Exception as e:
        print(f"[{idx+1}/{len(eins)}] ⚠️ Exception for {ein}: {e}")

    time.sleep(1)  # Respectful to the API (throttles ~1/sec)