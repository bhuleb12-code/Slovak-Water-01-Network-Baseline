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
# Load dataset
# ---------------------------------------------------------

print("=" * 60)
print("SLOVAK WATER SCADA — TEMPORAL BASELINE")
print("=" * 60)

print("\nLoading processed dataset...")

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values("timestamp").reset_index(drop=True)


# ---------------------------------------------------------
# Define chronological periods
# ---------------------------------------------------------

print("\nCreating chronological periods...")

start = df["timestamp"].min()
end = df["timestamp"].max()

total_duration = end - start

print(f"Dataset start:       {start}")
print(f"Dataset end:         {end}")
print(f"Total duration:      {total_duration}")


# ---------------------------------------------------------
# Chronological 70/15/15 split
# ---------------------------------------------------------

n = len(df)

train_end = int(n * 0.70)
validation_end = int(n * 0.85)

train = df.iloc[:train_end].copy()
validation = df.iloc[train_end:validation_end].copy()
test = df.iloc[validation_end:].copy()


# ---------------------------------------------------------
# Split summary
# ---------------------------------------------------------

print("\nCHRONOLOGICAL SPLIT")
print("-" * 60)

print(
    f"Training:    {len(train):,} rows "
    f"({len(train) / n * 100:.1f}%)"
)

print(
    f"Validation:  {len(validation):,} rows "
    f"({len(validation) / n * 100:.1f}%)"
)

print(
    f"Test:        {len(test):,} rows "
    f"({len(test) / n * 100:.1f}%)"
)


# ---------------------------------------------------------
# Period boundaries
# ---------------------------------------------------------

print("\nPERIOD BOUNDARIES")
print("-" * 60)

print(
    f"Training:    {train['timestamp'].min()} "
    f"→ {train['timestamp'].max()}"
)

print(
    f"Validation:  {validation['timestamp'].min()} "
    f"→ {validation['timestamp'].max()}"
)

print(
    f"Test:        {test['timestamp'].min()} "
    f"→ {test['timestamp'].max()}"
)


# ---------------------------------------------------------
# Target distribution by period
# ---------------------------------------------------------

print("\nTARGET DISTRIBUTION BY PERIOD")
print("-" * 60)


def target_summary(data, name):

    counts = data["fault_d7"].value_counts().sort_index()

    positive = int(counts.get(1, 0))
    negative = int(counts.get(0, 0))

    positive_pct = positive / len(data) * 100

    print(
        f"\n{name}"
    )

    print(
        f"  fault_d7=0: {negative:,} "
        f"({negative / len(data) * 100:.2f}%)"
    )

    print(
        f"  fault_d7=1: {positive:,} "
        f"({positive_pct:.2f}%)"
    )


target_summary(train, "TRAINING")
target_summary(validation, "VALIDATION")
target_summary(test, "TEST")


# ---------------------------------------------------------
# Positive episode counts by period
# ---------------------------------------------------------

print("\nPOSITIVE LABEL EPISODES BY PERIOD")
print("-" * 60)


def count_positive_episodes(data):

    s = data["fault_d7"]

    return int(
        ((s == 1) & (s.shift(1, fill_value=0) == 0)).sum()
    )


print(
    f"Training positive episodes:   "
    f"{count_positive_episodes(train)}"
)

print(
    f"Validation positive episodes: "
    f"{count_positive_episodes(validation)}"
)

print(
    f"Test positive episodes:       "
    f"{count_positive_episodes(test)}"
)


# ---------------------------------------------------------
# Boundary check
# ---------------------------------------------------------

print("\nBOUNDARY CHECK")
print("-" * 60)

print(
    "Training ends before validation:",
    train["timestamp"].max() < validation["timestamp"].min()
)

print(
    "Validation ends before test:",
    validation["timestamp"].max() < test["timestamp"].min()
)


# ---------------------------------------------------------
# Completion
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("TEMPORAL BASELINE COMPLETE")
print("=" * 60)