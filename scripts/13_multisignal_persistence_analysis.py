import pandas as pd
import numpy as np
from pathlib import Path


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

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "signal_risk_ranking.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

TARGET = "fault_d7"

EXCLUDE_COLUMNS = [
    "timestamp",
    TARGET
]


# ============================================================
# HEADER
# ============================================================

print()
print("=" * 110)
print("SIGNAL RISK RANKING")
print("=" * 110)


# ============================================================
# LOAD DATA
# ============================================================

print()
print("Loading processed dataset...")

df = pd.read_csv(
    INPUT_FILE,
    parse_dates=["timestamp"]
)

df = (
    df
    .sort_values("timestamp")
    .reset_index(drop=True)
)

print(f"Input records: {len(df):,}")


# ============================================================
# SIGNAL SELECTION
# ============================================================

signals = [
    column
    for column in df.columns
    if column not in EXCLUDE_COLUMNS
]

print(f"Signals analysed: {len(signals)}")


# ============================================================
# BASELINE
# ============================================================

baseline_fault_rate = df[TARGET].mean()

print()
print("=" * 110)
print("BASELINE")
print("=" * 110)

print(
    f"Overall 7-day fault rate: "
    f"{baseline_fault_rate * 100:.2f}%"
)


# ============================================================
# SIGNAL RISK ANALYSIS
# ============================================================

results = []


for signal in signals:

    series = df[signal]

    # --------------------------------------------------------
    # P95 threshold
    # --------------------------------------------------------

    p95 = series.quantile(0.95)

    deviation = series > p95

    deviation_count = int(deviation.sum())

    deviation_share = (
        deviation.mean() * 100
    )

    # --------------------------------------------------------
    # Fault rates
    # --------------------------------------------------------

    if deviation_count > 0:

        fault_when_deviation = (
            df.loc[deviation, TARGET]
            .mean()
        )

    else:

        fault_when_deviation = np.nan


    no_deviation = ~deviation

    if no_deviation.sum() > 0:

        fault_without_deviation = (
            df.loc[no_deviation, TARGET]
            .mean()
        )

    else:

        fault_without_deviation = np.nan


    # --------------------------------------------------------
    # Lift
    # --------------------------------------------------------

    if (
        pd.notna(fault_when_deviation)
        and
        pd.notna(fault_without_deviation)
        and
        fault_without_deviation > 0
    ):

        lift = (
            fault_when_deviation
            /
            fault_without_deviation
        )

    else:

        lift = np.nan


    # --------------------------------------------------------
    # Baseline-relative risk
    # --------------------------------------------------------

    if baseline_fault_rate > 0:

        baseline_relative_rate = (
            fault_when_deviation
            /
            baseline_fault_rate
        )

    else:

        baseline_relative_rate = np.nan


    # --------------------------------------------------------
    # Fault observations during deviation
    # --------------------------------------------------------

    if deviation_count > 0:

        fault_observations = int(
            df.loc[deviation, TARGET].sum()
        )

    else:

        fault_observations = 0


    # --------------------------------------------------------
    # Multi-signal participation
    #
    # Reuse Step 12 output when available.
    # --------------------------------------------------------

    multisignal_file = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "multisignal_deviation_analysis.csv"
    )

    multi_signal_events = np.nan
    multi_signal_participation = np.nan

    if multisignal_file.exists():

        try:

            multi_df = pd.read_csv(
                multisignal_file
            )

            row = multi_df[
                multi_df["signal"] == signal
            ]

            if not row.empty:

                if "multi_signal_events" in row.columns:

                    multi_signal_events = (
                        row.iloc[0]["multi_signal_events"]
                    )

                if (
                    "multi_signal_participation_percent"
                    in row.columns
                ):

                    multi_signal_participation = (
                        row.iloc[0][
                            "multi_signal_participation_percent"
                        ]
                    )

        except Exception:

            pass


    # --------------------------------------------------------
    # Risk classification
    # --------------------------------------------------------

    if (
        pd.notna(lift)
        and lift >= 1.25
        and deviation_share >= 1.0
    ):

        risk_class = "HIGH"

    elif (
        pd.notna(lift)
        and lift >= 1.10
    ):

        risk_class = "MODERATE"

    elif (
        pd.notna(lift)
        and lift >= 1.00
    ):

        risk_class = "WEAK"

    else:

        risk_class = "LOW"


    # --------------------------------------------------------
    # Append result
    # --------------------------------------------------------

    results.append(
        {
            "signal": signal,
            "p95_threshold": p95,
            "deviation_observations": deviation_count,
            "deviation_share_percent": deviation_share,
            "fault_rate_when_deviation": (
                fault_when_deviation
                * 100
            ),
            "fault_rate_without_deviation": (
                fault_without_deviation
                * 100
            ),
            "lift": lift,
            "baseline_relative_fault_rate": (
                baseline_relative_rate
                * 100
            ),
            "fault_observations_during_deviation":
                fault_observations,
            "multi_signal_events":
                multi_signal_events,
            "multi_signal_participation_percent":
                multi_signal_participation,
            "risk_class":
                risk_class
        }
    )


# ============================================================
# CREATE RESULTS DATAFRAME
# ============================================================

results_df = pd.DataFrame(results)


# ============================================================
# RANKING
# ============================================================

results_df = results_df.sort_values(
    by=[
        "risk_class",
        "lift",
        "fault_rate_when_deviation",
        "deviation_observations"
    ],
    ascending=[
        True,
        False,
        False,
        False
    ]
)


# Explicit risk ordering
risk_order = {
    "HIGH": 1,
    "MODERATE": 2,
    "WEAK": 3,
    "LOW": 4
}

results_df["_risk_order"] = (
    results_df["risk_class"]
    .map(risk_order)
)

results_df = results_df.sort_values(
    by=[
        "_risk_order",
        "lift"
    ],
    ascending=[
        True,
        False
    ]
)

results_df = results_df.drop(
    columns=["_risk_order"]
)

results_df = results_df.reset_index(
    drop=True
)

results_df["risk_rank"] = (
    results_df.index + 1
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# CONSOLE REPORT
# ============================================================

print()
print("=" * 110)
print("SIGNAL RISK RANKING")
print("=" * 110)

print()

print(
    f"{'Rank':>4} "
    f"{'Signal':35} "
    f"{'Dev %':>8} "
    f"{'Fault|Dev':>11} "
    f"{'Lift':>8} "
    f"{'Risk':>10}"
)

print("-" * 110)


for _, row in results_df.iterrows():

    print(
        f"{int(row['risk_rank']):4d} "
        f"{row['signal']:35} "
        f"{row['deviation_share_percent']:7.2f}% "
        f"{row['fault_rate_when_deviation']:10.2f}% "
        f"{row['lift']:8.2f} "
        f"{row['risk_class']:>10}"
    )


# ============================================================
# HIGH-RISK SIGNALS
# ============================================================

high_risk = results_df[
    results_df["risk_class"] == "HIGH"
]

print()
print("=" * 110)
print("HIGH-RISK SIGNALS")
print("=" * 110)

if high_risk.empty:

    print()
    print("No signals met the high-risk criteria.")

else:

    print()

    for _, row in high_risk.iterrows():

        print(
            f"{row['signal']}: "
            f"lift={row['lift']:.2f}, "
            f"fault|deviation="
            f"{row['fault_rate_when_deviation']:.2f}%, "
            f"deviation share="
            f"{row['deviation_share_percent']:.2f}%"
        )


# ============================================================
# MULTI-SIGNAL INTERPRETATION
# ============================================================

multi_available = results_df[
    results_df["multi_signal_participation_percent"]
    .notna()
]

print()
print("=" * 110)
print("MULTI-SIGNAL PARTICIPATION")
print("=" * 110)

if not multi_available.empty:

    print()

    top_multi = (
        multi_available
        .sort_values(
            "multi_signal_participation_percent",
            ascending=False
        )
        .head(10)
    )

    for _, row in top_multi.iterrows():

        print(
            f"{row['signal']:35} "
            f"{row['multi_signal_participation_percent']:7.2f}%"
        )

else:

    print()
    print(
        "Multi-signal participation data "
        "was not available."
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 110)
print("SUMMARY")
print("=" * 110)

print()
print(
    f"Baseline fault rate: "
    f"{baseline_fault_rate * 100:.2f}%"
)

print(
    f"Signals analysed: "
    f"{len(results_df)}"
)

print(
    f"High-risk signals: "
    f"{len(high_risk)}"
)

print(
    f"Moderate-risk signals: "
    f"{(results_df['risk_class'] == 'MODERATE').sum()}"
)

print(
    f"Weak-risk signals: "
    f"{(results_df['risk_class'] == 'WEAK').sum()}"
)

print(
    f"Low-risk signals: "
    f"{(results_df['risk_class'] == 'LOW').sum()}"
)

print()
print(
    "IMPORTANT: This ranking describes association, "
    "not causation."
)

print(
    "A high-risk signal should therefore be interpreted "
    "as a useful monitoring or predictive candidate, "
    "not as proof that the signal causes faults."
)

print()
print("Results saved to:")
print(OUTPUT_FILE)

print()
print("=" * 110)
print("SIGNAL RISK RANKING COMPLETE")
print("=" * 110)