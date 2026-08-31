# Slovak Water – Phase 1: SCADA Fault Risk Analysis

## Project Overview

This project analyses industrial SCADA telemetry from a Slovak water infrastructure environment to investigate whether deviations in operational signals are associated with increased fault risk.

The project represents **Phase 1** of an industrial analytics workflow, moving from raw operational telemetry through data preparation, baseline analysis, signal-level risk analysis, and business-oriented visualisation in Power BI.

The objective was not simply to identify faults, but to examine whether deviations from baseline signal behaviour provide useful evidence of subsequent fault activity.

---

## Business Question

> **Which SCADA signals provide the strongest evidence of increased fault risk following a deviation from their baseline behaviour?**

The analysis was designed to support the identification of signals that may warrant greater attention in future condition-monitoring and predictive-maintenance work.

---

## Analytical Objective

The analysis sought to:

1. Establish baseline behaviour for the available SCADA signals.
2. Identify deviations from baseline conditions.
3. Examine the relationship between signal deviations and subsequent fault activity.
4. Compare fault association across individual signals.
5. Evaluate deviation persistence and lead-time characteristics.
6. Combine multiple indicators into a broader deviation-risk assessment.
7. Communicate the results through an interactive Power BI dashboard.

---

## Analytical Approach

The project followed a structured analytical workflow:

**Raw SCADA Data → Data Preparation → Baseline Modelling → Signal Comparison → Deviation Analysis → Fault Association → Risk Analysis → Power BI Dashboard**

Key analytical components included:

* Dataset preparation and cleaning
* Network-level baseline analysis
* Signal-level comparison
* Temporal baseline analysis
* Baseline fault modelling
* Temporal naive baseline comparison
* Target persistence analysis
* Baseline-relative fault association
* Deviation episode persistence analysis
* Deviation lead-time analysis
* Multisignal deviation analysis
* Combined deviation risk scoring
* Evidence summarisation

---

## Key Findings

The signal-level analysis showed that **SCADA signals do not provide equal levels of evidence regarding fault risk**.

The strongest Average Fault Lift values were observed for signals including:

| Signal                        | Average Fault Lift |
| ----------------------------- | -----------------: |
| `gw_temp_site2_anomaly_score` |               1.38 |
| `326417_ws_temp`              |               1.37 |
| `319235_ws_temp`              |               1.37 |
| `326416_ws_vigor`             |               1.33 |
| `279805_ws_vigor`             |               1.32 |

Lower-ranked signals showed substantially weaker associations, including:

* `238045_ws_temp` — approximately 1.00
* `gw_lvl_site2_anomaly_score` — approximately 0.97

The analysis therefore provides evidence that **signal selection matters when investigating deviation-based fault risk**.

These results should be interpreted as analytical associations rather than proof of causality or a production-ready predictive-maintenance model.

---

## Power BI Dashboard

The project includes a Power BI dashboard designed to communicate the signal-level findings to a management and operational audience.

The dashboard includes:

* **Average Fault Lift by Signal**
* **Deviation Rate by Signal**
* **Fault Rate After Deviation by Signal**
* **Distribution of Signal Deviations**
* **Signal Risk Evidence**

The dashboard provides both a visual overview and detailed signal-level evidence.

### Dashboard File

`data/processed/Slovak_Water_SCADA_Baseline.pbix`

---

## Data

The repository contains:

### Raw Data

Located in:

`data/raw/`

This includes the source dataset and associated documentation.

### Processed Data

Located in:

`data/processed/`

Key analytical outputs include:

* `scada_clean_hourly.csv`
* `baseline_relative_fault_association.csv`
* `signal_risk_ranking.csv`
* `combined_deviation_risk_score.csv`
* `deviation_episode_persistence.csv`
* `deviation_lead_time_analysis.csv`
* `multisignal_deviation_analysis.csv`

---

## Tools and Technologies

* **Python**
* **Pandas**
* **Statistical analysis**
* **Time-series analysis**
* **SCADA telemetry analysis**
* **Power BI**
* **Git / GitHub**

---

## Limitations

The results represent an analytical investigation of the available SCADA data and should not be interpreted as a deployed predictive-maintenance system.

In particular:

* Association does not establish causation.
* Signal deviations may have multiple operational explanations.
* The analysis is based on the available observation period and data quality.
* Further temporal validation would be required before operational deployment.
* Additional domain knowledge and engineering validation would be required before using the results for automated intervention or maintenance decisions.

---

## Project Status

**Phase 1 — Complete**

The first phase established the analytical foundation for examining SCADA signal deviations and their relationship with fault risk.

Future phases can build on this foundation through additional validation, predictive modelling, operationalisation, and deployment-oriented analytics.

---

## Author

**Blessing Taurai Chikowore**

Industrial Analytics | Data Analysis | Python | SQL | Power BI | SCADA Analytics

---

## Repository

This repository contains the analytical code, processed outputs, supporting reports, and Power BI dashboard for the project.
