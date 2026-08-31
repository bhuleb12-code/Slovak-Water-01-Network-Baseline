import pandas as pd
import numpy as np

print("=" * 60)
print("SLOVAK WATER SCADA — TARGET CONSTRUCTION ANALYSIS")
print("=" * 60)

INPUT_FILE = "data/processed/scada_clean_hourly.csv"

print("\nLoading processed dataset...")

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

target = df["fault_d7"]

# ============================================================
# BASIC TIMELINE
# ============================================================

print("\nDATASET TIMELINE")
print("-" * 60)

print("Start:", df["timestamp"].min())
print("End:  ", df["timestamp"].max())
print("Rows:", len(df))

# ============================================================
# FIND ALL TARGET TRANSITIONS
# ============================================================

print("\n")
print("=" * 60)
print("TARGET TRANSITIONS")
print("=" * 60)

transition = target.ne(target.shift())

transition_rows = df.loc[
    transition,
    ["timestamp", "fault_d7"]
].copy()

transition_rows["previous_fault"] = target.shift(
    1
).loc[transition].values

transition_rows["transition"] = (
    transition_rows["previous_fault"]
    .astype("Int64")
    .astype(str)
    + " -> "
    + transition_rows["fault_d7"]
    .astype(str)
)

transition_rows = transition_rows[
    transition_rows["previous_fault"].notna()
]

print()
print("Number of transitions:", len(transition_rows))

print()
print(
    transition_rows[
        [
            "timestamp",
            "previous_fault",
            "fault_d7",
            "transition"
        ]
    ].to_string(index=False)
)

# ============================================================
# POSITIVE EPISODES
# ============================================================

print("\n")
print("=" * 60)
print("POSITIVE EPISODE BOUNDARIES")
print("=" * 60)

runs = target.ne(target.shift()).cumsum()

episodes = (
    df.assign(run=runs)
      .groupby("run")
      .agg(
          label=("fault_d7", "first"),
          start=("timestamp", "first"),
          end=("timestamp", "last"),
          observations=("fault_d7", "size")
      )
)

positive = episodes[
    episodes["label"] == 1
].copy()

positive["duration_hours"] = positive["observations"]

positive["duration_days"] = (
    positive["duration_hours"] / 24
)

print()
print(
    positive[
        [
            "start",
            "end",
            "duration_hours",
            "duration_days"
        ]
    ].to_string(index=False)
)

# ============================================================
# CHECK FOR 7-DAY STRUCTURE
# ============================================================

print("\n")
print("=" * 60)
print("7-DAY STRUCTURE CHECK")
print("=" * 60)

durations = positive["duration_hours"]

print()
print("Positive episode durations in hours:")
print(
    durations
    .value_counts()
    .sort_index()
    .to_string()
)

print()
print("Positive episode durations in days:")
print(
    positive["duration_days"]
    .round(2)
    .value_counts()
    .sort_index()
    .to_string()
)

# ============================================================
# TRANSITION SPACING
# ============================================================

print("\n")
print("=" * 60)
print("POSITIVE EPISODE TRANSITION SPACING")
print("=" * 60)

starts = positive["start"]

start_gaps = (
    starts
    .diff()
    .dt.total_seconds()
    / 3600
)

positive["hours_since_previous_positive_start"] = start_gaps.values

print()
print(
    positive[
        [
            "start",
            "end",
            "duration_days",
            "hours_since_previous_positive_start"
        ]
    ].to_string(index=False)
)

# ============================================================
# LABEL AROUND TRANSITIONS
# ============================================================

print("\n")
print("=" * 60)
print("OBSERVATIONS AROUND TARGET TRANSITIONS")
print("=" * 60)

transition_indices = df.index[
    df["fault_d7"].ne(df["fault_d7"].shift())
]

windows = []

for idx in transition_indices:

    if idx == 0:
        continue

    start = max(0, idx - 3)
    end = min(len(df), idx + 4)

    window = df.loc[
        start:end - 1,
        ["timestamp", "fault_d7"]
    ].copy()

    window["transition_index"] = idx

    windows.append(window)

if windows:

    transition_windows = pd.concat(
        windows,
        ignore_index=True
    )

    print()
    print(
        transition_windows.to_string(index=False)
    )

# ============================================================
# CHECK WHETHER POSITIVE LABELS FORM 7-DAY BLOCKS
# ============================================================

print("\n")
print("=" * 60)
print("7-DAY BLOCK ANALYSIS")
print("=" * 60)

df["date"] = df["timestamp"].dt.date

daily = (
    df.groupby("date")
      .agg(
          observations=("fault_d7", "size"),
          positive_hours=("fault_d7", "sum")
      )
)

daily["positive_pct"] = (
    daily["positive_hours"]
    / daily["observations"]
    * 100
)

print()
print("Days with 100% positive labels:",
      (daily["positive_pct"] == 100).sum())

print("Days with 0% positive labels:",
      (daily["positive_pct"] == 0).sum())

print("Mixed-label days:",
      (
          (daily["positive_pct"] > 0)
          & (daily["positive_pct"] < 100)
      ).sum())

print()
print("Daily target profile:")
print(
    daily.head(30).to_string()
)

# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 60)
print("TARGET CONSTRUCTION SUMMARY")
print("=" * 60)

print()
print(
    "Positive observations:",
    int((target == 1).sum())
)

print(
    "Negative observations:",
    int((target == 0).sum())
)

print(
    "Positive episodes:",
    len(positive)
)

print(
    "Shortest positive episode:",
    positive["duration_days"].min(),
    "days"
)

print(
    "Longest positive episode:",
    positive["duration_days"].max(),
    "days"
)

print(
    "Median positive episode:",
    positive["duration_days"].median(),
    "days"
)

print()
print(
    "NOTE: This analysis does not assume that fault_d7 is"
)
print(
    "a genuine 7-day-ahead forecasting target."
)
print(
    "It is intended to establish how the target was constructed"
)
print(
    "and whether temporal persistence is inherent in the label."
)

print("\n")
print("=" * 60)
print("TARGET CONSTRUCTION ANALYSIS COMPLETE")
print("=" * 60)