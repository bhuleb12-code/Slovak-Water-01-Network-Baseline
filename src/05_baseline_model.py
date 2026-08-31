import os
import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report,
)


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/processed/scada_clean_hourly.csv"
OUTPUT_FILE = "data/processed/baseline_model_results.csv"

TARGET = "fault_d7"

TEST_SIZE = 0.15
VALIDATION_SIZE = 0.15


# ============================================================
# HEADER
# ============================================================

print("=" * 60)
print("SLOVAK WATER SCADA — BASELINE MODEL")
print("=" * 60)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading processed dataset...")

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce"
)

df = df.sort_values("timestamp").reset_index(drop=True)


# ============================================================
# CHRONOLOGICAL SPLIT
# ============================================================

print("\nCreating chronological train/validation/test split...")

n = len(df)

train_end = int(n * (1 - VALIDATION_SIZE - TEST_SIZE))
validation_end = int(n * (1 - TEST_SIZE))

train = df.iloc[:train_end].copy()
validation = df.iloc[train_end:validation_end].copy()
test = df.iloc[validation_end:].copy()

print("\nSPLIT SUMMARY")
print("-" * 60)

print(f"Training:    {len(train):,} rows")
print(f"Validation:  {len(validation):,} rows")
print(f"Test:        {len(test):,} rows")


# ============================================================
# FEATURES / TARGET
# ============================================================

features = [c for c in df.columns if c not in ["timestamp", TARGET]]

X_train = train[features]
y_train = train[TARGET]

X_validation = validation[features]
y_validation = validation[TARGET]

X_test = test[features]
y_test = test[TARGET]


print("\nFEATURES")
print("-" * 60)

print(f"Feature count: {len(features)}")

for i, feature in enumerate(features, start=1):
    print(f"{i:2d}. {feature}")


# ============================================================
# TARGET PROFILE
# ============================================================

print("\nTARGET DISTRIBUTION")
print("-" * 60)

for name, y in [
    ("Training", y_train),
    ("Validation", y_validation),
    ("Test", y_test),
]:

    counts = y.value_counts().sort_index()

    print(f"\n{name}")

    for label, count in counts.items():
        pct = count / len(y) * 100
        print(f"  fault_d7={label}: {count:,} ({pct:.2f}%)")


# ============================================================
# MODEL PIPELINE
# ============================================================

print("\nBuilding Logistic Regression pipeline...")

pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        ),
        (
            "model",
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42
            )
        ),
    ]
)


# ============================================================
# TRAIN
# ============================================================

print("\nTraining baseline model...")

pipeline.fit(X_train, y_train)

print("Training complete.")


# ============================================================
# EVALUATION FUNCTION
# ============================================================

def evaluate_model(name, X, y):

    predictions = pipeline.predict(X)
    probabilities = pipeline.predict_proba(X)[:, 1]

    accuracy = accuracy_score(y, predictions)
    precision = precision_score(y, predictions, zero_division=0)
    recall = recall_score(y, predictions, zero_division=0)
    f1 = f1_score(y, predictions, zero_division=0)
    roc_auc = roc_auc_score(y, probabilities)
    pr_auc = average_precision_score(y, probabilities)

    cm = confusion_matrix(y, predictions)

    print("\n" + "=" * 60)
    print(f"{name.upper()} RESULTS")
    print("=" * 60)

    print(f"Accuracy:          {accuracy:.4f}")
    print(f"Precision:         {precision:.4f}")
    print(f"Recall:            {recall:.4f}")
    print(f"F1 Score:          {f1:.4f}")
    print(f"ROC-AUC:           {roc_auc:.4f}")
    print(f"PR-AUC:            {pr_auc:.4f}")

    print("\nConfusion Matrix")
    print("-" * 30)

    print(cm)

    print("\nClassification Report")
    print("-" * 30)

    print(
        classification_report(
            y,
            predictions,
            digits=4,
            zero_division=0
        )
    )

    return {
        "dataset": name,
        "observations": len(y),
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "true_negative": cm[0, 0],
        "false_positive": cm[0, 1],
        "false_negative": cm[1, 0],
        "true_positive": cm[1, 1],
    }


# ============================================================
# EVALUATE
# ============================================================

results = []

results.append(
    evaluate_model(
        "Training",
        X_train,
        y_train
    )
)

results.append(
    evaluate_model(
        "Validation",
        X_validation,
        y_validation
    )
)

results.append(
    evaluate_model(
        "Test",
        X_test,
        y_test
    )
)


# ============================================================
# SAVE RESULTS
# ============================================================

results_df = pd.DataFrame(results)

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# MODEL COEFFICIENTS
# ============================================================

print("\n" + "=" * 60)
print("MODEL COEFFICIENTS")
print("=" * 60)

model = pipeline.named_steps["model"]

coefficients = pd.DataFrame({
    "feature": features,
    "coefficient": model.coef_[0]
})

coefficients["abs_coefficient"] = (
    coefficients["coefficient"].abs()
)

coefficients = coefficients.sort_values(
    "abs_coefficient",
    ascending=False
)

print(
    coefficients[
        ["feature", "coefficient"]
    ].to_string(index=False)
)


# ============================================================
# COMPLETE
# ============================================================

print("\nResults saved to:")
print(os.path.abspath(OUTPUT_FILE))

print("\n" + "=" * 60)
print("BASELINE MODEL COMPLETE")
print("=" * 60)