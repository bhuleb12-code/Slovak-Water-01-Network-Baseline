import pandas as pd
import numpy as np

print("=" * 60)
print("SLOVAK WATER SCADA — TARGET PERSISTENCE ANALYSIS")
print("=" * 60)

INPUT_FILE = "data/processed/scada_clean_hourly.csv"
OUTPUT_FILE = "data/processed/target_persistence_analysis.csv"

print("\nLoading processed dataset...")

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

target = df["fault_d7"]

# ============================================================
# BASIC TARGET TRANSITIONS
# ============================================================

print("\nTARGET TRANSITIONS")
print("-" * 60)

previous = target.shift(1)

valid = previous.notna()

previous_valid = previous[valid]
current_valid = target[valid]

transitions = pd.crosstab(
    previous_valid,
    current_valid
)

print()
print("Transition matrix:")
print(transitions.to_string())

# ------------------------------------------------------------
# CONDITIONAL PROBABILITIES
# ------------------------------------------------------------

p_1_given_1 = (
    ((previous_valid == 1) & (current_valid == 1)).sum()
    / (previous_valid == 1).sum()
)

p_0_given_0 = (
    ((previous_valid == 0) & (current_valid == 0)).sum()
    / (previous_valid == 0).sum()
)

p_1_given_0 = (
    ((previous_valid == 0) & (current_valid == 1)).sum()
    / (previous_valid == 0).sum()
)

p_0_given_1 = (
    ((previous_valid == 1) & (current_valid == 0)).sum()
    / (previous_valid == 1).sum()
)

print()
print("Conditional probabilities:")
print(f"P(fault_t=1 | fault_t-1=1): {p_1_given_1:.4f}")
print(f"P(fault_t=0 | fault_t-1=0): {p_0_given_0:.4f}")
print(f"P(fault_t=1 | fault_t-1=0): {p_1_given_0:.4f}")
print(f"P(fault_t=0 | fault_t-1=1): {p_0_given_1:.4f}")

# ============================================================
# TARGET CHANGE RATE
# ============================================================

print("\n")
print("=" * 60)
print("TARGET CHANGE RATE")
print("=" * 60)

changes = target.ne(target.shift())

number_of_changes = changes.iloc[1:].sum()
number_of_transitions = len(target) - 1

change_rate = number_of_changes / number_of_transitions

print()
print("Total observations:", len(target))
print("Target transitions:", number_of_transitions)
print("Target state changes:", number_of_changes)
print(f"State change rate: {change_rate:.4%}")
print(f"State persistence rate: {1 - change_rate:.4%}")

# ============================================================
# RUN / EPISODE ANALYSIS
# ============================================================

print("\n")
print("=" * 60)
print("TARGET EPISODE ANALYSIS")
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

episodes["duration_hours"] = episodes["observations"]
episodes["duration_days"] = episodes["duration_hours"] / 24

positive = episodes[episodes["label"] == 1].copy()
negative = episodes[episodes["label"] == 0].copy()

print()
print("Total episodes:", len(episodes))
print("Positive episodes:", len(positive))
print("Negative episodes:", len(negative))

print()
print("POSITIVE EPISODES")
print("-" * 60)
print(
    positive[
        [
            "start",
            "end",
            "observations",
            "duration_days"
        ]
    ].to_string(index=False)
)

print()
print("POSITIVE EPISODE DURATION")
print("-" * 60)
print(
    positive["duration_days"]
    .describe()
    .round(2)
    .to_string()
)

print()
print("NEGATIVE EPISODE DURATION")
print("-" * 60)
print(
    negative["duration_days"]
    .describe()
    .round(2)
    .to_string()
)

# ============================================================
# PERSISTENCE AT MULTIPLE LAGS
# ============================================================

print("\n")
print("=" * 60)
print("TARGET PERSISTENCE BY LAG")
print("=" * 60)

lag_results = []

for lag in [1, 2, 3, 6, 12, 24, 48, 72, 168]:

    previous_target = target.shift(lag)

    valid = previous_target.notna()

    persistence = (
        target[valid].values
        == previous_target[valid].values
    ).mean()

    lag_results.append({
        "lag_hours": lag,
        "persistence_rate": persistence
    })

    print(
        f"Lag {lag:>3} hours: "
        f"{persistence:.4%}"
    )

# ============================================================
# PERSISTENCE BY TARGET STATE
# ============================================================

print("\n")
print("=" * 60)
print("STATE-SPECIFIC PERSISTENCE")
print("=" * 60)

state_results = []

for lag in [1, 6, 24, 72, 168]:

    lagged = target.shift(lag)

    valid = lagged.notna()

    current = target[valid]
    previous_state = lagged[valid]

    positive_previous = previous_state == 1
    negative_previous = previous_state == 0

    positive_persistence = (
        (current[positive_previous] == 1).mean()
        if positive_previous.sum() > 0
        else np.nan
    )

    negative_persistence = (
        (current[negative_previous] == 0).mean()
        if negative_previous.sum() > 0
        else np.nan
    )

    state_results.append({
        "lag_hours": lag,
        "positive_persistence": positive_persistence,
        "negative_persistence": negative_persistence
    })

    print()
    print(f"Lag: {lag} hours")
    print(
        "  Positive persistence:",
        f"{positive_persistence:.4%}"
    )
    print(
        "  Negative persistence:",
        f"{negative_persistence:.4%}"
    )

# ============================================================
# SAVE RESULTS
# ============================================================

lag_df = pd.DataFrame(lag_results)
state_df = pd.DataFrame(state_results)

summary = pd.DataFrame({
    "metric": [
        "total_observations",
        "target_changes",
        "change_rate",
        "persistence_rate",
        "total_episodes",
        "positive_episodes",
        "negative_episodes",
        "p_fault1_given_fault1",
        "p_fault0_given_fault0",
        "p_fault1_given_fault0",
        "p_fault0_given_fault1"
    ],
    "value": [
        len(target),
        number_of_changes,
        change_rate,
        1 - change_rate,
        len(episodes),
        len(positive),
        len(negative),
        p_1_given_1,
        p_0_given_0,
        p_1_given_0,
        p_0_given_1
    ]
})

summary.to_csv(
    OUTPUT_FILE,
    index=False
)

lag_output = "data/processed/target_persistence_by_lag.csv"
state_output = "data/processed/target_state_persistence_by_lag.csv"

lag_df.to_csv(lag_output, index=False)
state_df.to_csv(state_output, index=False)

print("\n")
print("=" * 60)
print("TARGET PERSISTENCE ANALYSIS COMPLETE")
print("=" * 60)

print()
print("Summary saved to:")
print(OUTPUT_FILE)

print()
print("Lag analysis saved to:")
print(lag_output)

print()
print("State-specific analysis saved to:")
print(state_output)