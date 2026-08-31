from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

OUTPUT_FILE = (
    PROCESSED_DIR
    / "baseline_results_evidence_summary.csv"
)

REPORT_FILE = (
    REPORTS_DIR
    / "project_1_baseline_summary.txt"
)


# ============================================================
# INPUT FILES
# ============================================================

FILES = {
    "baseline_model": PROCESSED_DIR / "baseline_model_results.csv",
    "temporal_naive": PROCESSED_DIR / "temporal_naive_baseline_results.csv",
    "target_persistence": PROCESSED_DIR / "target_persistence_analysis.csv",
    "signal_comparison": PROCESSED_DIR / "signal_comparison.csv",
    "baseline_relative": PROCESSED_DIR / "baseline_relative_fault_association.csv",
    "deviation_persistence": PROCESSED_DIR / "deviation_episode_persistence.csv",
    "lead_time": PROCESSED_DIR / "deviation_lead_time_analysis.csv",
    "multisignal": PROCESSED_DIR / "multisignal_deviation_analysis.csv",
    "combined_risk": PROCESSED_DIR / "combined_deviation_risk_score.csv",
}


# ============================================================
# HEADER
# ============================================================

print()
print("=" * 110)
print("PROJECT 1 — BASELINE RESULTS & EVIDENCE SUMMARY")
print("=" * 110)

print()
print("Purpose:")
print(
    "Consolidate the analytical evidence generated during the "
    "baseline investigation."
)

print(
    "No new predictive model is fitted in this step."
)


# ============================================================
# LOAD MAIN DATASET
# ============================================================

MAIN_DATASET = PROCESSED_DIR / "scada_clean_hourly.csv"

print()
print("=" * 110)
print("DATASET BASELINE")
print("=" * 110)

df = pd.read_csv(MAIN_DATASET)

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = (
    df
    .sort_values("timestamp")
    .reset_index(drop=True)
)

baseline_fault_rate = (
    df["fault_d7"].mean() * 100
)

print()
print(f"Observations:          {len(df):,}")
print(f"Start:                 {df['timestamp'].min()}")
print(f"End:                   {df['timestamp'].max()}")
print(f"Fault observations:    {(df['fault_d7'] == 1).sum():,}")
print(f"Non-fault observations:{(df['fault_d7'] == 0).sum():,}")
print(f"Baseline fault rate:   {baseline_fault_rate:.2f}%")


# ============================================================
# HELPER
# ============================================================

loaded = {}

for name, path in FILES.items():

    if path.exists():

        try:

            loaded[name] = pd.read_csv(path)

            print(
                f"Loaded {name}: "
                f"{len(loaded[name]):,} rows"
            )

        except Exception as error:

            print(
                f"WARNING: Could not load {name}: {error}"
            )

    else:

        print(
            f"WARNING: Missing result file: {path}"
        )


# ============================================================
# EVIDENCE RECORDS
# ============================================================

evidence = []


def add_evidence(
    category,
    finding,
    result,
    interpretation,
    status
):

    evidence.append(
        {
            "category": category,
            "finding": finding,
            "result": result,
            "interpretation": interpretation,
            "evidence_status": status
        }
    )


# ============================================================
# 1. BASELINE PREVALENCE
# ============================================================

add_evidence(
    "Baseline prevalence",
    "Overall 7-day fault rate",
    f"{baseline_fault_rate:.2f}%",
    (
        "This is the reference prevalence against which "
        "predictive and risk-based results must be evaluated."
    ),
    "ESTABLISHED"
)


# ============================================================
# 2. BASELINE MODEL
# ============================================================

if "baseline_model" in loaded:

    result = loaded["baseline_model"]

    add_evidence(
        "Predictive baseline",
        "Baseline model results",
        f"{len(result)} result records",
        (
            "The baseline predictive model provides the "
            "initial benchmark for subsequent modelling."
        ),
        "ESTABLISHED"
    )


# ============================================================
# 3. TEMPORAL NAIVE BASELINE
# ============================================================

if "temporal_naive" in loaded:

    result = loaded["temporal_naive"]

    add_evidence(
        "Temporal baseline",
        "Temporal-naive benchmark",
        f"{len(result)} result records",
        (
            "The temporal-naive benchmark establishes how much "
            "predictive information can be obtained from temporal "
            "persistence alone."
        ),
        "ESTABLISHED"
    )


# ============================================================
# 4. TARGET PERSISTENCE
# ============================================================

if "target_persistence" in loaded:

    result = loaded["target_persistence"]

    add_evidence(
        "Target behaviour",
        "Fault-label persistence",
        f"{len(result)} result records",
        (
            "The target exhibits temporal persistence, meaning "
            "predictive performance must be interpreted against "
            "a strong temporal baseline."
        ),
        "ESTABLISHED"
    )


# ============================================================
# 5. SIGNAL ASSOCIATION
# ============================================================

if "baseline_relative" in loaded:

    result = loaded["baseline_relative"].copy()

    if "Lift" in result.columns:

        result["Lift"] = pd.to_numeric(
            result["Lift"],
            errors="coerce"
        )

    elif "lift" in result.columns:

        result["lift"] = pd.to_numeric(
            result["lift"],
            errors="coerce"
        )

        result["Lift"] = result["lift"]

    if len(result) > 0:

        top_row = result.loc[
            result["Lift"].idxmax()
        ]

        signal_column = (
            "Signal"
            if "Signal" in result.columns
            else "signal"
        )

        signal_name = top_row[signal_column]

        top_lift = top_row["Lift"]

        add_evidence(
            "Signal association",
            "Strongest baseline-relative signal",
            f"{signal_name} — lift {top_lift:.2f}",
            (
                "Several signals show elevated fault association "
                "when deviating from their baseline."
            ),
            "ESTABLISHED"
        )


# ============================================================
# 6. DEVIATION PERSISTENCE
# ============================================================

if "deviation_persistence" in loaded:

    result = loaded["deviation_persistence"]

    add_evidence(
        "Temporal signal behaviour",
        "Deviation episode persistence",
        f"{len(result):,} deviation episodes",
        (
            "Abnormal signal conditions persist for variable "
            "durations, including multi-hour and multi-day episodes."
        ),
        "ESTABLISHED"
    )


# ============================================================
# 7. LEAD TIME
# ============================================================

if "lead_time" in loaded:

    result = loaded["lead_time"]

    add_evidence(
        "Temporal predictive evidence",
        "Fault following deviation",
        (
            "24h: 89.12%; "
            "48h: 91.00%; "
            "72h: 91.26%; "
            "7d: 94.26%"
        ),
        (
            "Deviation episodes are frequently followed by "
            "a positive fault label within the analysed horizons."
        ),
        "ESTABLISHED — ASSOCIATIONAL"
    )


# ============================================================
# 8. MULTI-SIGNAL ASSOCIATION
# ============================================================

if "multisignal" in loaded:

    result = loaded["multisignal"]

    add_evidence(
        "Multi-signal behaviour",
        "Simultaneous signal deviations",
        (
            "Hours with >=2 deviations: 1,332; "
            "fault rate: 89.11%"
        ),
        (
            "Concurrent abnormal conditions are associated "
            "with higher fault prevalence than the overall baseline."
        ),
        "ESTABLISHED — ASSOCIATIONAL"
    )


# ============================================================
# 9. COMBINED RISK
# ============================================================

if "combined_risk" in loaded:

    result = loaded["combined_risk"].copy()

    if "fault_lift" in result.columns:

        result["fault_lift"] = pd.to_numeric(
            result["fault_lift"],
            errors="coerce"
        )

        result["fault_rate_percent"] = pd.to_numeric(
            result["fault_rate_percent"],
            errors="coerce"
        )

        result = result.dropna(
            subset=["fault_lift"]
        )

        if len(result) > 0:

            highest = result.loc[
                result["fault_lift"].idxmax()
            ]

            add_evidence(
                "Combined risk",
                "Deviation-count risk gradient",
                (
                    f"Maximum observed lift: "
                    f"{highest['fault_lift']:.2f}; "
                    f"fault rate: "
                    f"{highest['fault_rate_percent']:.2f}%"
                ),
                (
                    "Fault prevalence increases as the number "
                    "of simultaneous deviations increases."
                ),
                "ESTABLISHED — ASSOCIATIONAL"
            )


# ============================================================
# 10. LIMITATIONS
# ============================================================

add_evidence(
    "Limitation",
    "High baseline fault prevalence",
    f"{baseline_fault_rate:.2f}% positive rate",
    (
        "Raw fault percentages must not be interpreted without "
        "comparison with the high baseline prevalence."
    ),
    "IMPORTANT"
)

add_evidence(
    "Limitation",
    "Association versus causation",
    "Signal deviation is associated with fault labels",
    (
        "The analysis does not establish that any signal "
        "causes the fault condition."
    ),
    "IMPORTANT"
)

add_evidence(
    "Limitation",
    "Target temporal persistence",
    "fault_d7 is temporally persistent",
    (
        "Apparent predictive performance may partly reflect "
        "the temporal structure of the target."
    ),
    "IMPORTANT"
)

add_evidence(
    "Limitation",
    "Out-of-sample generalisation",
    "Not established by this baseline",
    (
        "The baseline identifies promising predictors but does "
        "not establish their performance on genuinely unseen future data."
    ),
    "NOT ESTABLISHED"
)


# ============================================================
# FINAL BASELINE CONCLUSION
# ============================================================

add_evidence(
    "Final conclusion",
    "Project 1 baseline finding",
    "Predictive candidates identified",
    (
        "The baseline investigation establishes meaningful "
        "relationships between abnormal signal behaviour, "
        "temporal persistence, simultaneous deviations and "
        "the fault_d7 target. Several signals and multi-signal "
        "patterns warrant further predictive investigation."
    ),
    "BASELINE COMPLETE"
)


# ============================================================
# CREATE DATAFRAME
# ============================================================

summary_df = pd.DataFrame(evidence)


# ============================================================
# SAVE CSV
# ============================================================

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

summary_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# TEXT REPORT
# ============================================================

REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "PROJECT 1 — SLOVAK WATER SCADA\n"
    )

    file.write(
        "BASELINE RESULTS & EVIDENCE SUMMARY\n"
    )

    file.write(
        "=" * 90 + "\n\n"
    )

    file.write(
        "PURPOSE\n"
    )

    file.write(
        "This report consolidates the analytical evidence "
        "generated during the baseline investigation.\n"
    )

    file.write(
        "No new predictive model was fitted in Step 15.\n\n"
    )

    file.write(
        "DATASET\n"
    )

    file.write(
        f"Observations: {len(df):,}\n"
    )

    file.write(
        f"Start: {df['timestamp'].min()}\n"
    )

    file.write(
        f"End: {df['timestamp'].max()}\n"
    )

    file.write(
        f"Baseline fault rate: {baseline_fault_rate:.2f}%\n\n"
    )

    file.write(
        "KEY BASELINE FINDINGS\n"
    )

    file.write(
        "-" * 90 + "\n"
    )

    for _, row in summary_df.iterrows():

        file.write(
            f"\n[{row['evidence_status']}]\n"
        )

        file.write(
            f"Category: {row['category']}\n"
        )

        file.write(
            f"Finding: {row['finding']}\n"
        )

        file.write(
            f"Result: {row['result']}\n"
        )

        file.write(
            f"Interpretation: {row['interpretation']}\n"
        )

    file.write(
        "\n"
        + "=" * 90
        + "\n"
    )

    file.write(
        "PROJECT 1 BASELINE CONCLUSION\n"
    )

    file.write(
        "=" * 90 + "\n\n"
    )

    file.write(
        "The baseline investigation established that the "
        "Slovak Water SCADA dataset contains substantial "
        "temporal persistence and meaningful associations "
        "between abnormal signal behaviour and the fault_d7 "
        "target. Individual signal deviations, persistent "
        "deviation episodes and simultaneous deviations are "
        "all associated with elevated fault prevalence.\n\n"
    )

    file.write(
        "The analysis therefore identified several promising "
        "signals and multi-signal patterns for predictive "
        "monitoring. However, these results should be treated "
        "as baseline evidence rather than proof of causal or "
        "out-of-sample predictive performance.\n\n"
    )

    file.write(
        "PROJECT 1 STATUS: BASELINE COMPLETE\n"
    )


# ============================================================
# CONSOLE SUMMARY
# ============================================================

print()
print("=" * 110)
print("PROJECT 1 BASELINE CONCLUSION")
print("=" * 110)

print()
print("Baseline fault rate:")
print(f"  {baseline_fault_rate:.2f}%")

print()
print("Key findings:")

print(
    "  1. Target persistence is present."
)

print(
    "  2. Several signal deviations are associated "
    "with elevated fault risk."
)

print(
    "  3. Deviation episodes frequently precede "
    "positive fault labels."
)

print(
    "  4. Simultaneous deviations are associated "
    "with progressively higher fault prevalence."
)

print(
    "  5. Several signals are promising predictive candidates."
)

print()
print("Important limitations:")

print(
    "  - Association does not establish causation."
)

print(
    "  - High baseline fault prevalence affects interpretation."
)

print(
    "  - Temporal persistence must be considered."
)

print(
    "  - Genuine out-of-sample generalisation is not established "
    "by this baseline."
)

print()
print("=" * 110)
print("PROJECT 1 STATUS: BASELINE COMPLETE")
print("=" * 110)

print()
print("Evidence summary saved to:")
print(OUTPUT_FILE)

print()
print("Final baseline report saved to:")
print(REPORT_FILE)

print()

