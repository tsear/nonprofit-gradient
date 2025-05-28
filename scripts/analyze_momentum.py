import pandas as pd
from pathlib import Path
import numpy as np

# === Load the financial timeseries ===
df = pd.read_csv("data/processed/financial_timeseries.csv")
output_file = Path("data/processed/momentum_classification.csv")

# Ensure numeric types
df["REVENUE"] = pd.to_numeric(df["REVENUE"], errors="coerce")
df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce")

# Clean and drop nulls
df = df.dropna(subset=["REVENUE", "YEAR"])
df = df.sort_values(by=["EIN", "YEAR"])

results = []

# === Analyze by EIN ===
for ein, group in df.groupby("EIN"):
    org_name = group["ORG_NAME"].iloc[0]

    # Must have at least 6 years
    if len(group) < 6:
        continue

    revs = group["REVENUE"].tolist()
    years = group["YEAR"].tolist()

    recent = revs[-3:]  # most recent 3 years
    prior = revs[-6:-3]  # 3 years before that

    if sum(recent) < 1 or sum(prior) < 1:
        continue

    avg_recent = sum(recent) / len(recent)
    avg_prior = sum(prior) / len(prior)

    pct_change = (avg_recent - avg_prior) / avg_prior
    pct_change = round(pct_change * 100, 2)

    # === Normalized Momentum ===
    raw_momentum = (recent[2] - recent[1]) + (recent[1] - recent[0])
    normalized_momentum = raw_momentum / avg_recent
    normalized_momentum = round(normalized_momentum, 4)

    # Volatility = std / mean
    volatility = pd.Series(revs).std() / pd.Series(revs).mean()
    volatility = round(volatility, 3)

    # === Classify ===
    if volatility > 0.5:
        label = "turbulent"
    elif pct_change > 20 and normalized_momentum > 0:
        label = "strong_momentum_up"
    elif pct_change < -20 and normalized_momentum < 0:
        label = "strong_momentum_down"
    elif 5 < pct_change <= 20:
        label = "weak_up"
    elif -20 <= pct_change < -5:
        label = "weak_down"
    elif abs(pct_change) <= 5:
        label = "stable"
    else:
        label = "uncategorized"

    results.append({
        "EIN": ein,
        "ORG_NAME": org_name,
        "AVG_RECENT_REVENUE": int(avg_recent),
        "AVG_PRIOR_REVENUE": int(avg_prior),
        "PCT_CHANGE": pct_change,
        "MOMENTUM_SCORE": normalized_momentum,
        "VOLATILITY": volatility,
        "MOMENTUM_CLASS": label
    })

# Save results
out = pd.DataFrame(results)
out.to_csv(output_file, index=False)

print(f"✅ Momentum classification saved to {output_file}")
print(f"📊 Orgs classified: {len(out)}")