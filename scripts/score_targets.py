import pandas as pd
from pathlib import Path

input_file = Path("data/processed/org_master_profiles.csv")
output_file = Path("data/processed/org_master_profiles_scored.csv")

df = pd.read_csv(input_file)

def calculate_score(row):
    score = 0

    if row.get("IS_HOLLOW") is True or str(row.get("IS_HOLLOW")).lower() == "true":
        score += 40

    if row.get("IS_TURBULENT") is True or str(row.get("IS_TURBULENT")).lower() == "true":
        score += 30

    momentum = str(row.get("MOMENTUM_CLASS", "")).lower()
    if "down" in momentum:
        score += 20
    elif "turbulent" in momentum:
        score += 10

    size = str(row.get("SIZE_BUCKET", "")).lower()
    if size == "medium":
        score += 10
    elif size == "large":
        score += 15
    elif size == "major":
        score += 20

    return score

def assign_flag(score):
    if score >= 70:
        return "high_priority"
    elif score >= 50:
        return "watchlist"
    elif score >= 30:
        return "low_priority"
    else:
        return "not_a_fit"

df["PRIORITY_SCORE"] = df.apply(calculate_score, axis=1)
df["TARGET_FLAG"] = df["PRIORITY_SCORE"].apply(assign_flag)

df.to_csv(output_file, index=False)
print(f"✅ Saved scored file to {output_file}")