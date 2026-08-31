from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "input_model_potenc_predXfault7_A.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_FILE = PROCESSED_DIR / "scada_clean_hourly.csv"


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

print("=" * 60)
print("SLOVAK WATER SCADA — DATA PREPARATION")
print("=" * 60)

print("\nLoading raw dataset...")
df = pd.read_csv(RAW_FILE)

print(f"Raw rows: {len(df):,}")
print(f"Raw columns: {len(df.columns)}")


# ---------------------------------------------------------
# Parse timestamp
# ---------------------------------------------------------

print("\nParsing timestamps...")

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    format="%d-%m-%Y %H:%M"
)


# ---------------------------------------------------------
# Sort chronologically
# ---------------------------------------------------------

print("Sorting chronologically...")

df = df.sort_values("timestamp").reset_index(drop=True)


# ---------------------------------------------------------
# Data-quality checks
# ---------------------------------------------------------

print("\nRunning data-quality checks...")

duplicate_timestamps = df["timestamp"].duplicated().sum()

time_gaps = (
    df["timestamp"]
    .diff()
    .dropna()
)

non_hourly_gaps = (
    time_gaps != pd.Timedelta(hours=1)
).sum()


invalid_timestamps = df["timestamp"].isna().sum()


# ---------------------------------------------------------
# Target validation
# ---------------------------------------------------------

target_values = sorted(df["fault_d7"].dropna().unique().tolist())

invalid_target_values = [
    value for value in target_values
    if value not in [0, 1]
]


# ---------------------------------------------------------
# Create processed directory
# ---------------------------------------------------------

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# Save processed dataset
# ---------------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# Report
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("DATA QUALITY REPORT")
print("=" * 60)

print(f"Rows:                    {len(df):,}")
print(f"Columns:                 {len(df.columns)}")
print(f"Earliest timestamp:      {df['timestamp'].min()}")
print(f"Latest timestamp:        {df['timestamp'].max()}")
print(f"Chronological:           {df['timestamp'].is_monotonic_increasing}")
print(f"Duplicate timestamps:    {duplicate_timestamps}")
print(f"Non-hourly gaps:         {non_hourly_gaps}")
print(f"Invalid timestamps:      {invalid_timestamps}")
print(f"Target values:           {target_values}")
print(f"Invalid target values:   {invalid_target_values}")

print("\nMissing values by column:")

missing = df.isna().sum()

for column, count in missing.items():
    if count > 0:
        percentage = count / len(df) * 100
        print(
            f"  {column}: "
            f"{count:,} ({percentage:.2f}%)"
        )


print("\nTarget distribution:")

target_counts = df["fault_d7"].value_counts().sort_index()

for label, count in target_counts.items():
    percentage = count / len(df) * 100

    print(
        f"  fault_d7={label}: "
        f"{count:,} ({percentage:.2f}%)"
    )


print("\nProcessed dataset saved to:")
print(OUTPUT_FILE)

print("\n" + "=" * 60)
print("PREPARATION COMPLETE")
print("=" * 60)