from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "scada_clean_hourly.csv"
)


# ---------------------------------------------------------
# Load processed dataset
# ---------------------------------------------------------

print("=" * 60)
print("SLOVAK WATER SCADA — NETWORK BASELINE")
print("=" * 60)

print("\nLoading processed dataset...")

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])


# ---------------------------------------------------------
# Basic dataset profile
# ---------------------------------------------------------

print("\nDATASET PROFILE")
print("-" * 60)

print(f"Rows:                 {len(df):,}")
print(f"Columns:              {len(df.columns)}")
print(f"Start:                {df['timestamp'].min()}")
print(f"End:                  {df['timestamp'].max()}")
print(f"Duration (days):      {(df['timestamp'].max() - df['timestamp'].min()).days}")


# ---------------------------------------------------------
# Feature classification
# ---------------------------------------------------------

target = "fault_d7"
features = [c for c in df.columns if c not in ["timestamp", target]]


print("\nFEATURE INVENTORY")
print("-" * 60)

print(f"Target variable:      {target}")
print(f"Feature count:        {len(features)}")

for i, feature in enumerate(features, start=1):
    print(f"{i:2}. {feature}")


# ---------------------------------------------------------
# Missingness profile
# ---------------------------------------------------------

print("\nMISSINGNESS PROFILE")
print("-" * 60)

missing = pd.DataFrame({
    "missing": df[features].isna().sum(),
    "missing_pct": df[features].isna().mean() * 100
})

missing = missing.sort_values(
    "missing_pct",
    ascending=False
)

print(
    missing.round(2).to_string()
)


# ---------------------------------------------------------
# Descriptive statistics
# ---------------------------------------------------------

print("\nDESCRIPTIVE STATISTICS")
print("-" * 60)

stats = (
    df[features]
    .describe()
    .T[
        [
            "count",
            "mean",
            "std",
            "min",
            "25%",
            "50%",
            "75%",
            "max"
        ]
    ]
)

print(
    stats.round(2).to_string()
)


# ---------------------------------------------------------
# Target distribution
# ---------------------------------------------------------

print("\nTARGET DISTRIBUTION")
print("-" * 60)

target_counts = df[target].value_counts().sort_index()

for value, count in target_counts.items():
    pct = count / len(df) * 100

    print(
        f"{target}={value}: "
        f"{count:,} observations "
        f"({pct:.2f}%)"
    )


# ---------------------------------------------------------
# Monthly observation profile
# ---------------------------------------------------------

print("\nMONTHLY OBSERVATION PROFILE")
print("-" * 60)

df["month"] = df["timestamp"].dt.to_period("M").astype(str)

monthly = (
    df.groupby("month")
    .agg(
        observations=("timestamp", "size"),
        positive_labels=(target, "sum")
    )
)

monthly["positive_pct"] = (
    monthly["positive_labels"]
    / monthly["observations"]
    * 100
)

print(
    monthly.round(2).to_string()
)


# ---------------------------------------------------------
# Completion
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("NETWORK BASELINE PROFILE COMPLETE")
print("=" * 60)