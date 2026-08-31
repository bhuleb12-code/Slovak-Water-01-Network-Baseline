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

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "signal_comparison.csv"
)


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

print("=" * 60)
print("SLOVAK WATER SCADA — SIGNAL COMPARISON")
print("=" * 60)

print("\nLoading processed dataset...")

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])


# ---------------------------------------------------------
# Identify features
# ---------------------------------------------------------

target = "fault_d7"

features = [
    column
    for column in df.columns
    if column not in ["timestamp", target]
]


# ---------------------------------------------------------
# Compare signals by target class
# ---------------------------------------------------------

results = []

for feature in features:

    normal = df.loc[
        df[target] == 0,
        feature
    ].dropna()

    fault = df.loc[
        df[target] == 1,
        feature
    ].dropna()

    result = {
        "feature": feature,

        "normal_count": len(normal),
        "fault_count": len(fault),

        "normal_missing_pct": (
            df.loc[df[target] == 0, feature].isna().mean() * 100
        ),

        "fault_missing_pct": (
            df.loc[df[target] == 1, feature].isna().mean() * 100
        ),

        "normal_mean": normal.mean(),
        "fault_mean": fault.mean(),

        "normal_median": normal.median(),
        "fault_median": fault.median(),

        "normal_p75": normal.quantile(0.75),
        "fault_p75": fault.quantile(0.75),

        "normal_p90": normal.quantile(0.90),
        "fault_p90": fault.quantile(0.90),

        "normal_p95": normal.quantile(0.95),
        "fault_p95": fault.quantile(0.95),

        "normal_nonzero_pct": (
            (normal > 0).mean() * 100
        ),

        "fault_nonzero_pct": (
            (fault > 0).mean() * 100
        ),
    }

    # Difference in means
    result["mean_difference"] = (
        result["fault_mean"]
        - result["normal_mean"]
    )

    # Ratio of means
    if result["normal_mean"] != 0:
        result["mean_ratio"] = (
            result["fault_mean"]
            / result["normal_mean"]
        )
    else:
        result["mean_ratio"] = None

    # Difference in non-zero frequency
    result["nonzero_difference_pp"] = (
        result["fault_nonzero_pct"]
        - result["normal_nonzero_pct"]
    )

    results.append(result)


# ---------------------------------------------------------
# Create results dataframe
# ---------------------------------------------------------

comparison = pd.DataFrame(results)


# ---------------------------------------------------------
# Rank signals
# ---------------------------------------------------------

comparison["abs_mean_difference"] = (
    comparison["mean_difference"].abs()
)

comparison = comparison.sort_values(
    "abs_mean_difference",
    ascending=False
).reset_index(drop=True)


# ---------------------------------------------------------
# Save results
# ---------------------------------------------------------

comparison.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# Display main results
# ---------------------------------------------------------

display_columns = [
    "feature",
    "normal_mean",
    "fault_mean",
    "mean_difference",
    "normal_median",
    "fault_median",
    "normal_p90",
    "fault_p90",
    "normal_nonzero_pct",
    "fault_nonzero_pct",
    "nonzero_difference_pp",
]


print("\nSIGNAL COMPARISON")
print("-" * 60)

print(
    comparison[display_columns]
    .round(2)
    .to_string(index=False)
)


# ---------------------------------------------------------
# Missingness comparison
# ---------------------------------------------------------

print("\nMISSINGNESS COMPARISON")
print("-" * 60)

missing_columns = [
    "feature",
    "normal_missing_pct",
    "fault_missing_pct",
]

print(
    comparison[missing_columns]
    .round(2)
    .sort_values(
        "fault_missing_pct",
        ascending=False
    )
    .to_string(index=False)
)


# ---------------------------------------------------------
# Completion
# ---------------------------------------------------------

print("\nResults saved to:")
print(OUTPUT_FILE)

print("\n" + "=" * 60)
print("SIGNAL COMPARISON COMPLETE")
print("=" * 60)