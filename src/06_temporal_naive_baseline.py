import pandas as pd
import numpy as np

print("=" * 60)
print("SLOVAK WATER SCADA — TEMPORAL NAIVE BASELINES")
print("=" * 60)

INPUT_FILE = "data/processed/scada_clean_hourly.csv"
OUTPUT_FILE = "data/processed/temporal_naive_baseline_results.csv"

print("\nLoading processed dataset...")

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

n = len(df)

train_end = int(n * 0.70)
validation_end = int(n * 0.85)

train = df.iloc[:train_end].copy()
validation = df.iloc[train_end:validation_end].copy()
test = df.iloc[validation_end:].copy()

print("\nCHRONOLOGICAL SPLIT")
print("-" * 60)
print("Training:   ", len(train), "rows")
print("Validation: ", len(validation), "rows")
print("Test:       ", len(test), "rows")


def calculate_metrics(y_true, y_pred):

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    tp = ((y_true == 1) & (y_pred == 1)).sum()
    tn = ((y_true == 0) & (y_pred == 0)).sum()
    fp = ((y_true == 0) & (y_pred == 1)).sum()
    fn = ((y_true == 1) & (y_pred == 0)).sum()

    accuracy = (tp + tn) / len(y_true)

    if tp + fp > 0:
        precision = tp / (tp + fp)
    else:
        precision = 0.0

    if tp + fn > 0:
        recall = tp / (tp + fn)
    else:
        recall = 0.0

    if precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = 0.0

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp
    }


results = []


# ============================================================
# MAJORITY CLASS
# ============================================================

print("\n")
print("=" * 60)
print("MAJORITY-CLASS BASELINE")
print("=" * 60)

majority_class = train["fault_d7"].mode()[0]

print()
print("Majority class learned from training data:", majority_class)

for name, data in [
    ("Training", train),
    ("Validation", validation),
    ("Test", test)
]:

    predictions = np.full(len(data), majority_class)

    metrics = calculate_metrics(
        data["fault_d7"],
        predictions
    )

    results.append({
        "model": "Majority",
        "period": name,
        **metrics
    })

    print()
    print(name)
    print("-" * 30)
    print("Accuracy: ", round(metrics["accuracy"], 4))
    print("Precision:", round(metrics["precision"], 4))
    print("Recall:   ", round(metrics["recall"], 4))
    print("F1 Score: ", round(metrics["f1"], 4))


# ============================================================
# PREVIOUS-HOUR PERSISTENCE
# ============================================================

print("\n")
print("=" * 60)
print("PREVIOUS-HOUR PERSISTENCE BASELINE")
print("=" * 60)

for name, data in [
    ("Training", train),
    ("Validation", validation),
    ("Test", test)
]:

    predictions = data["fault_d7"].shift(1)

    valid = predictions.notna()

    y_true = data.loc[valid, "fault_d7"]
    y_pred = predictions.loc[valid]

    metrics = calculate_metrics(y_true, y_pred)

    results.append({
        "model": "Previous-hour",
        "period": name,
        **metrics
    })

    print()
    print(name)
    print("-" * 30)
    print("Accuracy: ", round(metrics["accuracy"], 4))
    print("Precision:", round(metrics["precision"], 4))
    print("Recall:   ", round(metrics["recall"], 4))
    print("F1 Score: ", round(metrics["f1"], 4))

    print()
    print("Confusion Matrix")
    print("-" * 30)
    print("[[", metrics["tn"], metrics["fp"], "]")
    print(" [", metrics["fn"], metrics["tp"], "]]")


# ============================================================
# PREVIOUS-24-HOUR PERSISTENCE
# ============================================================

print("\n")
print("=" * 60)
print("24-HOUR PERSISTENCE BASELINE")
print("=" * 60)

for name, data in [
    ("Training", train),
    ("Validation", validation),
    ("Test", test)
]:

    predictions = data["fault_d7"].shift(24)

    valid = predictions.notna()

    y_true = data.loc[valid, "fault_d7"]
    y_pred = predictions.loc[valid]

    metrics = calculate_metrics(y_true, y_pred)

    results.append({
        "model": "Previous-24h",
        "period": name,
        **metrics
    })

    print()
    print(name)
    print("-" * 30)
    print("Accuracy: ", round(metrics["accuracy"], 4))
    print("Precision:", round(metrics["precision"], 4))
    print("Recall:   ", round(metrics["recall"], 4))
    print("F1 Score: ", round(metrics["f1"], 4))

    print()
    print("Confusion Matrix")
    print("-" * 30)
    print("[[", metrics["tn"], metrics["fp"], "]")
    print(" [", metrics["fn"], metrics["tp"], "]]")


# ============================================================
# SAVE RESULTS
# ============================================================

results_df = pd.DataFrame(results)

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n")
print("=" * 60)
print("TEMPORAL NAIVE BASELINE SUMMARY")
print("=" * 60)

print()

print(
    results_df[
        [
            "model",
            "period",
            "accuracy",
            "precision",
            "recall",
            "f1"
        ]
    ].to_string(index=False)
)

print()
print("Results saved to:")
print(OUTPUT_FILE)

print("\n")
print("=" * 60)
print("TEMPORAL NAIVE BASELINES COMPLETE")
print("=" * 60)