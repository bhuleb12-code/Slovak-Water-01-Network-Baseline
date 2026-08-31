"""
Step 9 — Baseline-Relative Fault Association

Purpose
-------
Quantify whether observations above each signal's empirical P95
operating baseline are associated with an increased probability
of a fault occurring within the next 7 days.

Input
-----
data/processed/scada_clean_hourly.csv

Output
------
data/processed/baseline_relative_fault_association.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

INPUT_FILE = Path("data/processed/scada_clean_hourly.csv")
OUTPUT_FILE = Path(
    "data/processed/baseline_relative_fault_association.csv"
)


# -------------------------------------------------------------------
# Load data
# -------------------------------------------------------------------

df = pd.read_csv(
    INPUT_FILE,
    parse_dates=["timestamp"]
)

# Signals only
EXCLUDE_COLUMNS = {"timestamp", "fault_d7"}

signals = [
    column
    for column in df.columns
    if column not in EXCLUDE_COLUMNS
]


# -------------------------------------------------------------------
# Overall baseline fault rate
# -------------------------------------------------------------------

overall_fault_rate = df["fault_d7"].mean()


# -------------------------------------------------------------------
# Signal-level association analysis
# -------------------------------------------------------------------

results = []

for signal in signals:

    # Empirical operating baseline
    p95 = df[signal].quantile(0.95)

    # Deviation indicator
    deviation = df[signal] > p95

    deviation_count = int(deviation.sum())
    deviation_rate = deviation.mean()

    # Fault probability following deviation
    if deviation_count > 0:
        fault_rate_deviation = df.loc[
            deviation, "fault_d7"
        ].mean()

        faults_after_deviation = int(
            df.loc[deviation, "fault_d7"].sum()
        )
    else:
        fault_rate_deviation = np.nan
        faults_after_deviation = 0

    # Fault probability without deviation
    non_deviation = ~deviation
    non_deviation_count = int(non_deviation.sum())

    if non_deviation_count > 0:
        fault_rate_no_deviation = df.loc[
            non_deviation, "fault_d7"
        ].mean()
    else:
        fault_rate_no_deviation = np.nan

    # Lift
    if (
        pd.notna(fault_rate_no_deviation)
        and fault_rate_no_deviation > 0
    ):
        lift = (
            fault_rate_deviation
            / fault_rate_no_deviation
        )
    else:
        lift = np.nan

    results.append(
        {
            "signal": signal,
            "p95_baseline": p95,
            "deviation_observations": deviation_count,
            "deviation_rate": deviation_rate,
            "fault_rate_after_deviation": fault_rate_deviation,
            "fault_rate_without_deviation": fault_rate_no_deviation,
            "lift": lift,
            "faults_after_deviation": faults_after_deviation,
            "overall_fault_rate": overall_fault_rate,
        }
    )


# -------------------------------------------------------------------
# Results
# -------------------------------------------------------------------

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    "lift",
    ascending=False
)


# -------------------------------------------------------------------
# Save
# -------------------------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# -------------------------------------------------------------------
# Console summary
# -------------------------------------------------------------------

print()
print("BASELINE-RELATIVE FAULT ASSOCIATION")
print("=" * 110)

print(
    f"Input records: {len(df):,}"
)

print(
    f"Overall 7-day fault rate: "
    f"{overall_fault_rate * 100:.2f}%"
)

print()
print(
    f"{'Signal':35} "
    f"{'P95':>10} "
    f"{'Dev Obs':>9} "
    f"{'Dev %':>9} "
    f"{'Fault|Dev':>11} "
    f"{'Fault|NoDev':>13} "
    f"{'Lift':>9}"
)

print("-" * 110)

for _, row in results_df.iterrows():

    print(
        f"{row['signal']:35} "
        f"{row['p95_baseline']:10.2f} "
        f"{int(row['deviation_observations']):9d} "
        f"{row['deviation_rate'] * 100:8.2f}% "
        f"{row['fault_rate_after_deviation'] * 100:10.2f}% "
        f"{row['fault_rate_without_deviation'] * 100:12.2f}% "
        f"{row['lift']:9.2f}"
    )


print()
print("=" * 110)
print(f"Results saved to: {OUTPUT_FILE}")
print()