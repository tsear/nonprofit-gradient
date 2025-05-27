import pandas as pd
from pathlib import Path

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
    if len(group) < 5:
        continue  # too little history to say much

    revs = group["REVENUE"].tolist()
    years = group["YEAR"].tolist()

    # Split into recent and prior
    if len(revs) < 6:
        continue

    recent = revs[-3:]  # most recent 3 years
    prior = revs[-6:-3]  # 3 years before that

    # Skip orgs with $0 or None in both periods
    if sum(recent) < 1 or sum(prior) < 1:
        continue

    avg_recent = sum(recent) / len(recent)
    avg_prior = sum(prior) / len(prior)
    pct_change = (avg_recent - avg_prior) / avg_prior

    # Raw 2-step momentum score
    momentum_score = (recent[2] - recent[1]) + (recent[1] - recent[0])

    # Volatility score
    volatility = pd.Series(revs).std() / pd.Series(revs).mean()

    # === Classify ===
    if volatility > 0.5:
        label = "turbulent"
    elif pct_change > 0.2 and momentum_score > 0:
        label = "strong_momentum_up"
    elif pct_change < -0.2 and momentum_score < 0:
        label = "strong_momentum_down"
    elif 0.05 < pct_change <= 0.2:
        label = "weak_up"
    elif -0.2 <= pct_change < -0.05:
        label = "weak_down"
    elif abs(pct_change) <= 0.05:
        label = "stable"
    else:
        label = "uncategorized"

    results.append({
        "EIN": ein,
        "ORG_NAME": org_name,
        "AVG_RECENT_REVENUE": int(avg_recent),
        "AVG_PRIOR_REVENUE": int(avg_prior),
        "PCT_CHANGE": round(pct_change * 100, 2),
        "MOMENTUM_SCORE": int(momentum_score),
        "VOLATILITY": round(volatility, 2),
        "MOMENTUM_CLASS": label
    })

# Save results
out = pd.DataFrame(results)
out.to_csv(output_file, index=False)

print(f"✅ Momentum classification saved to {output_file}")
print(f"📊 Orgs classified: {len(out)}")