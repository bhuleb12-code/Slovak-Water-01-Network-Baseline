import pandas as pd
from pathlib import Path

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

INPUT_FILE = Path("data/processed/scada_clean_hourly.csv")
OUTPUT_FILE = Path("data/processed/deviation_episode_persistence.csv")

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
# Detect P95 deviations
# -------------------------------------------------------------------

records = []

for signal in cols:

    threshold = df[signal].quantile(0.95)

    deviation = df[signal] > threshold

    # Identify consecutive deviation episodes.
    group_id = (deviation != deviation.shift()).cumsum()

    episode_groups = df.groupby(group_id)

    for _, group in episode_groups:

        if not deviation.loc[group.index].iloc[0]:
            continue

        start_time = group["timestamp"].iloc[0]
        end_time = group["timestamp"].iloc[-1]

        duration_hours = len(group)

        fault_rate = group["fault_d7"].mean() * 100

        peak_value = group[signal].max()

        records.append({
            "signal": signal,
            "threshold_p95": threshold,
            "start_time": start_time,
            "end_time": end_time,
            "duration_hours": duration_hours,
            "peak_value": peak_value,
            "fault_rate_percent": fault_rate
        })

# -------------------------------------------------------------------
# Build result
# -------------------------------------------------------------------

results_df = pd.DataFrame(records)

if results_df.empty:
    print("No deviation episodes detected.")
else:

    results_df = results_df.sort_values(
        ["duration_hours", "start_time"],
        ascending=[False, True]
    ).reset_index(drop=True)

# -------------------------------------------------------------------
# Save results
# -------------------------------------------------------------------

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)

# -------------------------------------------------------------------
# Console summary
# -------------------------------------------------------------------

print()
print("DEVIATION EPISODE PERSISTENCE")
print("=" * 110)

print(f"Input records: {len(df):,}")
print(f"Signals analysed: {len(cols)}")
print(f"Deviation episodes detected: {len(results_df):,}")

if not results_df.empty:

    print()
    print("EPISODE DURATION DISTRIBUTION")
    print("-" * 70)

    print(
        results_df["duration_hours"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print()
    print("LONGEST DEVIATION EPISODES")
    print("-" * 110)

    display_cols = [
        "signal",
        "start_time",
        "end_time",
        "duration_hours",
        "peak_value",
        "fault_rate_percent"
    ]

    print(
        results_df
        .nlargest(20, "duration_hours")[display_cols]
        .to_string(index=False)
    )

    print()
    print("EPISODE SUMMARY BY SIGNAL")
    print("-" * 110)

    summary = (
        results_df
        .groupby("signal")
        .agg(
            episodes=("signal", "size"),
            mean_duration_hours=("duration_hours", "mean"),
            max_duration_hours=("duration_hours", "max"),
            total_deviation_hours=("duration_hours", "sum"),
            mean_peak=("peak_value", "mean"),
            max_peak=("peak_value", "max"),
            mean_fault_rate=("fault_rate_percent", "mean")
        )
        .sort_values(
            "total_deviation_hours",
            ascending=False
        )
    )

    print(summary.to_string())

print()
print("=" * 110)
print(f"Results saved to: {OUTPUT_FILE}")