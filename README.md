# Slovak Water SCADA — Phase 1: Network Baseline

## Project Overview

This project analyses industrial SCADA telemetry from a Slovak water infrastructure environment to establish a baseline understanding of system behaviour and investigate whether deviations in operational signals are associated with elevated fault risk.

It represents **Phase 1 of a three-phase Slovak Water SCADA analytics programme**. The programme progresses from foundational telemetry analysis to leak-risk investigation and, subsequently, applied data science for operating-behaviour and anomaly detection.

### Analytical Programme

| Phase  | Project                                     | Focus                                                                   |
| ------ | ------------------------------------------- | ----------------------------------------------------------------------- |
| **01** | **Network Baseline**                        | Establish the SCADA and operational baseline                            |
| **02** | **Leak Anomaly Analysis**                   | Investigate telemetry behaviour associated with known leak-risk periods |
| **03** | **Operating Behaviour & Anomaly Detection** | Learn operating regimes and identify previously unknown deviations      |

This repository contains the work completed for **Phase 1**.

---

## Business Question

> **Which SCADA signals provide the strongest evidence of increased fault risk following a deviation from their baseline behaviour?**

The question was designed to establish which telemetry signals may warrant greater attention in subsequent condition-monitoring and predictive-maintenance analysis.

---

## Analytical Objective

The analysis sought to:

1. Establish baseline behaviour for the available SCADA signals.
2. Identify deviations from baseline operating conditions.
3. Examine the relationship between signal deviations and fault-risk observations.
4. Compare fault association across individual signals.
5. Investigate deviation persistence and temporal characteristics.
6. Examine whether simultaneous deviations across multiple signals provide stronger evidence of elevated risk.
7. Consolidate the evidence into an interpretable analytical baseline.
8. Communicate the findings through Power BI.

The objective was **not** to deploy a production fault-prediction system. It was to establish an evidence-based analytical foundation for subsequent phases.

---

## Analytical Approach

The project followed a structured workflow:

**Raw SCADA Telemetry → Data Preparation → Baseline Analysis → Signal Comparison → Deviation Analysis → Fault Association → Temporal Analysis → Multi-Signal Analysis → Evidence Consolidation → Power BI**

Key analytical components included:

* SCADA dataset preparation and cleaning
* Network-level baseline analysis
* Signal-level behavioural comparison
* Baseline-relative deviation analysis
* Fault-association analysis
* Temporal baseline comparison
* Target persistence analysis
* Deviation episode analysis
* Deviation lead-time analysis
* Multi-signal deviation analysis
* Combined deviation-risk assessment
* Evidence consolidation
* Business-oriented visualisation

The baseline deviation threshold used in the signal-level analysis was based on the **empirical 95th percentile (P95)** of each signal's observed distribution.

---

## Key Findings

The analysis showed that **SCADA signals do not provide equal levels of evidence regarding fault risk**.

Several signals exhibited stronger associations between P95-level deviations and elevated fault-risk observations than others.

Examples of the strongest observed average fault-lift values included:

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

The results therefore provide evidence that **signal selection matters when investigating deviation-based fault risk**.

The analysis also found evidence that:

* Persistent deviation episodes can provide additional temporal context.
* Simultaneous deviations across multiple signals are associated with elevated fault prevalence.
* The combination of multiple abnormal signals can provide stronger risk evidence than considering individual deviations in isolation.

These findings establish a basis for the subsequent analytical phases.

---

## Interpretation of Results

The results should be interpreted as **observational analytical associations**, rather than proof that a particular signal causes a fault or that the identified relationships will necessarily generalise to unseen operational periods.

The `fault_d7` variable represents a historical fault-proximity classification rather than a direct physical measurement of a fault occurring at the exact observation time. Consequently, the results are most appropriately viewed as evidence for further investigation rather than as evidence of a deployed predictive-maintenance model.

This distinction is important because the project is intended to demonstrate an analytical progression:

**Understand the system → identify useful signals → investigate temporal behaviour → develop stronger predictive or behavioural methods.**

---

## Power BI Dashboard

The project includes a Power BI dashboard designed to communicate the analytical findings to management and operational audiences.

The dashboard includes:

* **Average Fault Lift by Signal**
* **Deviation Rate by Signal**
* **Fault Rate After Deviation by Signal**
* **Distribution of Signal Deviations**
* **Signal Risk Evidence**

The dashboard provides both a high-level overview and detailed signal-level evidence.

### Dashboard File

```text
data/processed/Slovak_Water_SCADA_Baseline.pbix
```

---

## Data

### Raw Data

Source data and associated documentation are located in:

```text
data/raw/
```

### Processed Data

Analytical outputs are located in:

```text
data/processed/
```

Key outputs include:

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

This project is an analytical investigation of the available SCADA telemetry and should not be interpreted as a deployed predictive-maintenance system.

Key limitations include:

* Association does not establish causation.
* Signal deviations may have multiple operational explanations.
* The available observation period limits generalisation.
* The historical fault-proximity target has temporal characteristics that must be considered when interpreting predictive evidence.
* Further out-of-sample temporal validation would be required before claiming production-level predictive performance.
* Additional engineering and domain validation would be required before using the results for automated intervention or maintenance decisions.
* The analysis does not establish that the identified signals are physical causes of faults.

---

## Project Status

**Phase 1 — Complete**

Phase 1 established the analytical foundation for understanding the SCADA telemetry and investigating relationships between signal deviations and historical fault-risk observations.

The work provides the foundation for the subsequent phases of the Slovak Water SCADA analytics programme:

**Phase 1 → Network Baseline**

**Phase 2 → Leak Anomaly Analysis**

**Phase 3 → Operating Behaviour & Anomaly Detection**

---

## Relationship to the Broader Programme

This repository is intentionally maintained as a **standalone project** while forming part of a larger analytical sequence.

The three projects use the Slovak Water SCADA environment as a common industrial analytics context, but each phase addresses a different analytical question.

Phase 1 establishes the baseline.

Phase 2 investigates known leak-risk behaviour.

Phase 3 moves beyond the known fault target to learn system operating behaviour and identify previously unknown deviations.

---

## Author

**Blessing Taurai Chikowore**

Industrial Analytics | Data Analysis | Python | SQL | Power BI | SCADA Analytics

---

## Repository

This repository contains the analytical code, processed outputs, supporting documentation, and Power BI dashboard associated with **Phase 1 of the Slovak Water SCADA Analytics programme**.

