import json
import pandas as pd
from pathlib import Path

input_dir = Path("data/financials_by_ein")
output_file = Path("data/processed/financial_timeseries.csv")
output_file.parent.mkdir(parents=True, exist_ok=True)

records = []

for file in input_dir.glob("*.json"):
    ein = file.stem
    try:
        with open(file, "r") as f:
            data = json.load(f)

        if "error" in data and data["error"] == "Not Found":
            continue

        org_name = data.get("organization", {}).get("name", "Unknown")

        for filing in data.get("filings_with_data", []):
            year = filing.get("tax_prd_yr")
            revenue = filing.get("totrevenue")
            expenses = filing.get("totfuncexpns")
            assets = filing.get("totassetsend")
            program = filing.get("totprgmrevnue")
            contributions = filing.get("totcntrbgfts")

            # Safely calculate program_pct
            try:
                revenue_val = float(revenue) if revenue not in [None, "", "null"] else 0
                program_val = float(program) if program not in [None, "", "null"] else 0
                program_pct = (program_val / revenue_val) * 100 if revenue_val > 0 else None
            except:
                program_pct = None

            if all(v in [None, 0, "", "null"] for v in [revenue, expenses, assets, program, contributions]):
                continue  # Skip completely empty records

            records.append({
                "EIN": ein,
                "ORG_NAME": org_name,
                "YEAR": year,
                "REVENUE": revenue,
                "EXPENSES": expenses,
                "ASSETS": assets,
                "PROGRAM_REVENUE": program,
                "CONTRIBUTIONS": contributions,
                "PROGRAM_PCT": round(program_pct, 2) if program_pct is not None else None
            })

    except Exception as e:
        print(f"⚠️ Skipped {ein}: {e}")
        continue

df = pd.DataFrame(records)
df = df.sort_values(by=["EIN", "YEAR"], ascending=[True, False])
df.to_csv(output_file, index=False)

print(f"✅ Flattened financials saved to {output_file}")
print(f"📊 Total records: {len(df)}")
print(f"📁 Unique EINs: {df['EIN'].nunique()}")