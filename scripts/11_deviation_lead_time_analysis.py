import pandas as pd
from pathlib import Path

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

INPUT_FILE = Path("data/processed/scada_clean_hourly.csv")
OUTPUT_FILE = Path("data/processed/deviation_lead_time_analysis.csv")

# -------------------------------------------------------------------
# Load data
# -------------------------------------------------------------------

df = pd.read_csv(INPUT_FILE, parse_dates=["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

cols = [
    c for c in df.columns
    if c not in ["timestamp", "fault_d7"]
]

# -------------------------------------------------------------------
# Detect P95 deviation episodes
# -------------------------------------------------------------------

episodes = []

for signal in cols:

    threshold = df[signal].quantile(0.95)

    deviation = df[signal] > threshold

    # Identify consecutive deviation periods.
    group_id = (deviation != deviation.shift()).cumsum()

    for _, group in df.groupby(group_id):

        if not deviation.loc[group.index].iloc[0]:
            continue

        start_time = group["timestamp"].iloc[0]
        end_time = group["timestamp"].iloc[-1]

        duration_hours = len(group)

        peak_value = group[signal].max()

        # -----------------------------------------------------------
        # Look forward from deviation onset.
        # -----------------------------------------------------------

        future = df[df["timestamp"] > start_time]

        first_fault = future.loc[
            future["fault_d7"] == 1,
            "timestamp"
        ].min()

        hours_to_first_fault = None

        if pd.notna(first_fault):
            hours_to_first_fault = (
                first_fault - start_time
            ).total_seconds() / 3600

        # -----------------------------------------------------------
        # Fault exposure windows
        # -----------------------------------------------------------

        def fault_within(hours):

            window_end = start_time + pd.Timedelta(
                hours=hours
            )

            window = df[
                (df["timestamp"] >= start_time)
                & (df["timestamp"] <= window_end)
            ]

            return int(window["fault_d7"].eq(1).any())

        fault_24h = fault_within(24)
        fault_48h = fault_within(48)
        fault_72h = fault_within(72)
        fault_7d = fault_within(168)

        episodes.append({
            "signal": signal,
            "threshold_p95": threshold,
            "start_time": start_time,
            "end_time": end_time,
            "duration_hours": duration_hours,
            "peak_value": peak_value,
            "fault_within_24h": fault_24h,
            "fault_within_48h": fault_48h,
            "fault_within_72h": fault_72h,
            "fault_within_7d": fault_7d,
            "hours_to_first_fault": hours_to_first_fault
        })

# -------------------------------------------------------------------
# Results
# -------------------------------------------------------------------

results_df = pd.DataFrame(episodes)

if not results_df.empty:
    results_df = results_df.sort_values(
        ["signal", "start_time"]
    ).reset_index(drop=True)

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
print("DEVIATION LEAD-TIME ANALYSIS")
print("=" * 115)

print(f"Input records: {len(df):,}")
print(f"Signals analysed: {len(cols)}")
print(f"Deviation episodes analysed: {len(results_df):,}")

if not results_df.empty:

    print()
    print("OVERALL LEAD-TIME RESULTS")
    print("-" * 80)

    print(
        f"Fault within 24h : "
        f"{results_df['fault_within_24h'].mean() * 100:.2f}%"
    )

    print(
        f"Fault within 48h : "
        f"{results_df['fault_within_48h'].mean() * 100:.2f}%"
    )

    print(
        f"Fault within 72h : "
        f"{results_df['fault_within_72h'].mean() * 100:.2f}%"
    )

    print(
        f"Fault within 7d  : "
        f"{results_df['fault_within_7d'].mean() * 100:.2f}%"
    )

    valid_lead = results_df[
        results_df["hours_to_first_fault"].notna()
    ]

    if not valid_lead.empty:

        print()
        print("FIRST-FAULT LEAD TIME")
        print("-" * 80)

        print(
            f"Episodes followed by a fault: "
            f"{len(valid_lead):,}"
        )

        print(
            f"Median hours to first fault: "
            f"{valid_lead['hours_to_first_fault'].median():.2f}"
        )

        print(
            f"Mean hours to first fault: "
            f"{valid_lead['hours_to_first_fault'].mean():.2f}"
        )

        print(
            f"Minimum hours to first fault: "
            f"{valid_lead['hours_to_first_fault'].min():.2f}"
        )

        print(
            f"Maximum hours to first fault: "
            f"{valid_lead['hours_to_first_fault'].max():.2f}"
        )

    print()
    print("LEAD-TIME SUMMARY BY SIGNAL")
    print("-" * 115)

    summary = (
        results_df
        .groupby("signal")
        .agg(
            episodes=("signal", "size"),
            fault_24h=("fault_within_24h", "mean"),
            fault_48h=("fault_within_48h", "mean"),
            fault_72h=("fault_within_72h", "mean"),
            fault_7d=("fault_within_7d", "mean"),
            median_hours_to_fault=(
                "hours_to_first_fault",
                "median"
            ),
            mean_duration_hours=(
                "duration_hours",
                "mean"
            ),
            max_duration_hours=(
                "duration_hours",
                "max"
            )
        )
    )

    summary["fault_24h"] *= 100
    summary["fault_48h"] *= 100
    summary["fault_72h"] *= 100
    summary["fault_7d"] *= 100

    summary = summary.sort_values(
        "fault_7d",
        ascending=False
    )

    print(summary.to_string())

print()
print("=" * 115)
print(f"Results saved to: {OUTPUT_FILE}")