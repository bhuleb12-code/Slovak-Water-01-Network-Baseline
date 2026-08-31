from pathlib import Path

import numpy as np
import pandas as pd


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
    / "multisignal_deviation_analysis.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print()
print("=" * 110)
print("MULTI-SIGNAL DEVIATION SEVERITY AND FAULT ASSOCIATION")
print("=" * 110)

df = pd.read_csv(
    INPUT_FILE,
    parse_dates=["timestamp"]
)

df = (
    df
    .sort_values("timestamp")
    .reset_index(drop=True)
)

cols = [
    c for c in df.columns
    if c not in ["timestamp", "fault_d7"]
]

print()
print(f"Input records: {len(df):,}")
print(f"Signals analysed: {len(cols)}")


# ============================================================
# EMPIRICAL P95 DEVIATION FLAGS
# ============================================================

deviation_flags = pd.DataFrame(
    index=df.index
)

for column in cols:

    threshold = df[column].quantile(0.95)

    deviation_flags[column] = (
        df[column] > threshold
    ).astype(int)


# ============================================================
# SIMULTANEOUS DEVIATION COUNT
# ============================================================

df["deviation_count"] = (
    deviation_flags.sum(axis=1)
)


# ============================================================
# BASELINE FAULT RATE
# ============================================================

baseline_fault_rate = (
    df["fault_d7"].mean()
)


# ============================================================
# FAULT ASSOCIATION BY DEVIATION COUNT
# ============================================================

print()
print("=" * 110)
print("FAULT ASSOCIATION BY SIMULTANEOUS DEVIATION COUNT")
print("=" * 110)

print()

print(
    f"{'Deviation Count':>17} "
    f"{'Hours':>10} "
    f"{'Share %':>10} "
    f"{'Fault Rate':>12} "
    f"{'Lift':>10}"
)

print("-" * 65)

summary_rows = []

for count in sorted(
    df["deviation_count"].unique()
):

    subset = df[
        df["deviation_count"] == count
    ]

    hours = len(subset)

    share = (
        hours
        / len(df)
        * 100
    )

    fault_rate = (
        subset["fault_d7"].mean()
    )

    lift = (
        fault_rate
        / baseline_fault_rate
        if baseline_fault_rate > 0
        else np.nan
    )

    print(
        f"{count:17d} "
        f"{hours:10d} "
        f"{share:9.2f}% "
        f"{fault_rate * 100:11.2f}% "
        f"{lift:9.2f}"
    )

    summary_rows.append(
        {
            "deviation_count": count,
            "hours": hours,
            "share_percent": share,
            "fault_rate_percent": fault_rate * 100,
            "lift": lift
        }
    )

summary_df = pd.DataFrame(
    summary_rows
)


# ============================================================
# MULTI-SIGNAL EVENT SUMMARY
# ============================================================

print()
print("=" * 110)
print("MULTI-SIGNAL EVENT SUMMARY")
print("=" * 110)

multi_signal_mask = (
    df["deviation_count"] >= 2
)

multi_signal_hours = int(
    multi_signal_mask.sum()
)

multi_signal_fault_rate = (
    df.loc[
        multi_signal_mask,
        "fault_d7"
    ].mean()
)

multi_signal_lift = (
    multi_signal_fault_rate
    / baseline_fault_rate
)

print()

print(
    f"Baseline fault rate:              "
    f"{baseline_fault_rate * 100:.2f}%"
)

print(
    f"Hours with >=2 deviations:         "
    f"{multi_signal_hours:,}"
)

print(
    f"Share of all hours:                "
    f"{multi_signal_hours / len(df) * 100:.2f}%"
)

print(
    f"Fault rate when >=2 deviations:    "
    f"{multi_signal_fault_rate * 100:.2f}%"
)

print(
    f"Fault lift when >=2 deviations:    "
    f"{multi_signal_lift:.2f}"
)

print()

print(
    f"Maximum simultaneous deviations:   "
    f"{int(df['deviation_count'].max())}"
)


# ============================================================
# SIGNAL PARTICIPATION
# ============================================================

print()
print("=" * 110)
print("SIGNAL PARTICIPATION IN MULTI-SIGNAL EVENTS")
print("=" * 110)

participation_rows = []

for column in cols:

    total_deviations = int(
        deviation_flags[column].sum()
    )

    multi_signal_events = int(
        deviation_flags.loc[
            multi_signal_mask,
            column
        ].sum()
    )

    participation_pct = (
        multi_signal_events
        / total_deviations
        * 100
        if total_deviations > 0
        else np.nan
    )

    participation_rows.append(
        {
            "signal": column,
            "multi_signal_events": multi_signal_events,
            "total_deviation_events": total_deviations,
            "multi_signal_participation_percent":
                participation_pct
        }
    )

participation_df = (
    pd.DataFrame(participation_rows)
    .sort_values(
        "multi_signal_events",
        ascending=False
    )
)

print()

print(
    participation_df.to_string(
        index=False
    )
)


# ============================================================
# TOP MULTI-SIGNAL PERIODS
# ============================================================

print()
print("=" * 110)
print("TOP 20 MULTI-SIGNAL DEVIATION PERIODS")
print("=" * 110)

top_events = (
    df[
        [
            "timestamp",
            "fault_d7",
            "deviation_count"
        ]
    ]
    .sort_values(
        [
            "deviation_count",
            "timestamp"
        ],
        ascending=[
            False,
            True
        ]
    )
    .head(20)
)

print()

print(
    top_events.to_string(
        index=False
    )
)


# ============================================================
# SIGNAL COMPOSITION OF TOP EVENTS
# ============================================================

print()
print("=" * 110)
print("SIGNALS PRESENT IN HIGHEST-SEVERITY EVENTS")
print("=" * 110)

max_count = int(
    df["deviation_count"].max()
)

max_events = df[
    df["deviation_count"] == max_count
]

print()

print(
    f"Maximum deviation count: {max_count}"
)

for _, row in max_events.iterrows():

    active_signals = [
        column
        for column in cols
        if deviation_flags.loc[
            row.name,
            column
        ] == 1
    ]

    print()
    print(
        f"Timestamp: {row['timestamp']}"
    )

    print(
        f"Fault label: {int(row['fault_d7'])}"
    )

    print(
        "Signals:"
    )

    for signal in active_signals:
        print(
            f"  - {signal}"
        )


# ============================================================
# SAVE RESULTS
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

summary_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# COMPLETION
# ============================================================

print()
print("=" * 110)
print("MULTI-SIGNAL DEVIATION ANALYSIS COMPLETE")
print("=" * 110)

print()

print(
    "Results saved to:"
)

print(
    OUTPUT_FILE
)

print()