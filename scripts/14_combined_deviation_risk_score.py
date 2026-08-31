from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "scada_clean_hourly.csv"
)

MULTISIGNAL_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "multisignal_deviation_analysis.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "combined_deviation_risk_score.csv"
)


# ============================================================
# HEADER
# ============================================================

print()
print("=" * 110)
print("COMBINED DEVIATION RISK SCORE ANALYSIS")
print("=" * 110)


# ============================================================
# LOAD DATA
# ============================================================

print()
print("Loading processed dataset...")

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = (
    df
    .sort_values("timestamp")
    .reset_index(drop=True)
)

print(f"Input records: {len(df):,}")


# ============================================================
# LOAD MULTI-SIGNAL RESULTS
# ============================================================

if MULTISIGNAL_FILE.exists():

    print("Loading multi-signal deviation results...")

    multi = pd.read_csv(MULTISIGNAL_FILE)

    print(f"Multi-signal records loaded: {len(multi):,}")

else:

    print()
    print("WARNING: Multi-signal result file was not found.")
    print("The deviation score will be reconstructed from the")
    print("processed dataset.")


# ============================================================
# IDENTIFY SIGNALS
# ============================================================

exclude_columns = {
    "timestamp",
    "fault_d7"
}

signals = [
    column
    for column in df.columns
    if column not in exclude_columns
    and pd.api.types.is_numeric_dtype(df[column])
]

print()
print(f"Signals identified: {len(signals)}")


# ============================================================
# CALCULATE P95 BASELINES
# ============================================================

print()
print("=" * 110)
print("CALCULATING SIGNAL BASELINES")
print("=" * 110)

p95_values = {}

for signal in signals:

    value = df[signal].quantile(0.95)

    p95_values[signal] = value


# ============================================================
# BUILD DEVIATION MATRIX
# ============================================================

print()
print("Constructing deviation matrix...")

deviation_matrix = pd.DataFrame(index=df.index)

for signal in signals:

    threshold = p95_values[signal]

    deviation_matrix[signal] = (
        df[signal] > threshold
    )


# ============================================================
# COMBINED DEVIATION COUNT
# ============================================================

df["deviation_count"] = (
    deviation_matrix
    .sum(axis=1)
    .astype(int)
)


# ============================================================
# BASELINE FAULT RATE
# ============================================================

baseline_fault_rate = (
    df["fault_d7"]
    .mean()
    * 100
)


# ============================================================
# RISK BY DEVIATION COUNT
# ============================================================

print()
print("=" * 110)
print("FAULT RISK BY COMBINED DEVIATION COUNT")
print("=" * 110)

risk_rows = []

for count in sorted(df["deviation_count"].unique()):

    subset = df[
        df["deviation_count"] == count
    ]

    observations = len(subset)

    fault_rate = (
        subset["fault_d7"].mean()
        * 100
    )

    share = (
        observations
        / len(df)
        * 100
    )

    if baseline_fault_rate > 0:

        lift = (
            fault_rate
            / baseline_fault_rate
        )

    else:

        lift = np.nan

    risk_rows.append(
        {
            "deviation_count": int(count),
            "observations": observations,
            "share_percent": share,
            "fault_rate_percent": fault_rate,
            "fault_lift": lift
        }
    )


risk_df = pd.DataFrame(risk_rows)


# ============================================================
# RISK BAND
# ============================================================

def classify_risk(lift):

    if pd.isna(lift):
        return "UNKNOWN"

    if lift >= 1.25:
        return "HIGH"

    if lift >= 1.10:
        return "MODERATE"

    if lift >= 1.00:
        return "WEAK"

    return "LOW"


risk_df["risk_band"] = (
    risk_df["fault_lift"]
    .apply(classify_risk)
)


# ============================================================
# CONSOLE TABLE
# ============================================================

print()
print(
    f"{'Dev Count':>10}"
    f"{'Hours':>10}"
    f"{'Share %':>12}"
    f"{'Fault Rate':>15}"
    f"{'Lift':>12}"
    f"{'Risk':>12}"
)

print("-" * 75)

for _, row in risk_df.iterrows():

    print(
        f"{int(row['deviation_count']):>10}"
        f"{int(row['observations']):>10}"
        f"{row['share_percent']:>11.2f}%"
        f"{row['fault_rate_percent']:>14.2f}%"
        f"{row['fault_lift']:>11.2f}"
        f"{row['risk_band']:>12}"
    )


# ============================================================
# THRESHOLD GROUPS
# ============================================================

print()
print("=" * 110)
print("CUMULATIVE DEVIATION RISK")
print("=" * 110)

threshold_rows = []

max_count = int(
    df["deviation_count"].max()
)

for threshold in range(1, max_count + 1):

    subset = df[
        df["deviation_count"] >= threshold
    ]

    observations = len(subset)

    if observations == 0:
        continue

    fault_rate = (
        subset["fault_d7"].mean()
        * 100
    )

    share = (
        observations
        / len(df)
        * 100
    )

    lift = (
        fault_rate
        / baseline_fault_rate
        if baseline_fault_rate > 0
        else np.nan
    )

    threshold_rows.append(
        {
            "minimum_deviation_count": threshold,
            "observations": observations,
            "share_percent": share,
            "fault_rate_percent": fault_rate,
            "fault_lift": lift
        }
    )


threshold_df = pd.DataFrame(
    threshold_rows
)


print()
print(
    f"{'Minimum Deviations':>20}"
    f"{'Hours':>10}"
    f"{'Share %':>12}"
    f"{'Fault Rate':>15}"
    f"{'Lift':>12}"
)

print("-" * 75)

for _, row in threshold_df.iterrows():

    print(
        f"{int(row['minimum_deviation_count']):>20}"
        f"{int(row['observations']):>10}"
        f"{row['share_percent']:>11.2f}%"
        f"{row['fault_rate_percent']:>14.2f}%"
        f"{row['fault_lift']:>11.2f}"
    )


# ============================================================
# HIGH-RISK HOURS
# ============================================================

print()
print("=" * 110)
print("HIGHEST COMBINED-RISK PERIODS")
print("=" * 110)

top_periods = (
    df[
        [
            "timestamp",
            "fault_d7",
            "deviation_count"
        ]
    ]
    .sort_values(
        ["deviation_count", "timestamp"],
        ascending=[False, True]
    )
    .head(25)
)

print()
print(
    top_periods.to_string(
        index=False
    )
)


# ============================================================
# RISK CONCENTRATION
# ============================================================

print()
print("=" * 110)
print("RISK CONCENTRATION")
print("=" * 110)

for threshold in [1, 2, 3, 4]:

    subset = df[
        df["deviation_count"] >= threshold
    ]

    if len(subset) == 0:
        continue

    fault_rate = (
        subset["fault_d7"].mean()
        * 100
    )

    print()
    print(
        f"Hours with >= {threshold} deviations: "
        f"{len(subset):,}"
    )

    print(
        f"Share of dataset: "
        f"{len(subset) / len(df) * 100:.2f}%"
    )

    print(
        f"Fault rate: "
        f"{fault_rate:.2f}%"
    )

    print(
        f"Fault lift: "
        f"{fault_rate / baseline_fault_rate:.2f}"
    )


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 110)
print("COMBINED DEVIATION RISK SUMMARY")
print("=" * 110)

print()
print(
    f"Baseline fault rate: "
    f"{baseline_fault_rate:.2f}%"
)

print(
    f"Maximum simultaneous deviations: "
    f"{max_count}"
)

if len(risk_df) > 0:

    highest_risk_row = risk_df.loc[
        risk_df["fault_lift"].idxmax()
    ]

    print()
    print(
        "Highest observed deviation-count lift:"
    )

    print(
        f"  Deviation count: "
        f"{int(highest_risk_row['deviation_count'])}"
    )

    print(
        f"  Fault rate: "
        f"{highest_risk_row['fault_rate_percent']:.2f}%"
    )

    print(
        f"  Lift: "
        f"{highest_risk_row['fault_lift']:.2f}"
    )


# ============================================================
# SAVE RESULTS
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

risk_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SAVE CUMULATIVE RESULTS
# ============================================================

threshold_output = (
    OUTPUT_FILE.parent
    / "combined_deviation_cumulative_risk.csv"
)

threshold_df.to_csv(
    threshold_output,
    index=False
)


# ============================================================
# FINAL MESSAGE
# ============================================================

print()
print("=" * 110)
print("COMBINED DEVIATION RISK ANALYSIS COMPLETE")
print("=" * 110)

print()
print("Results saved to:")
print(OUTPUT_FILE)

print()
print("Cumulative results saved to:")
print(threshold_output)

print()

