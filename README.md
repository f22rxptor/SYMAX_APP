# 🧪 Symax Laboratories - AI & Automation Stock Assistant

An automated, rule-based Inventory Intelligence Assistant built for **Symax Laboratories Pvt. Ltd.** to analyze ERP stock datasets, handle data quality anomalies, manage multi-location inventory, and deliver accurate, deterministic natural language stock responses without LLM hallucination risks.

---

## 📌 Features

- **Natural Language Query Engine**: Search inventory using natural questions (e.g., *"What is the stock of n-Butyllithium 1.6 M Hexane?"* or *"What is the stock of CAS 109-72-8?"*).
- **Data Quality Pipeline**: Automatically handles location typos (`HYD`, `Hyderbad`, `BLR`), standardizes concentration strings (molarity & percentages), and quarantines non-positive quantities and unknown locations into an audit log.
- **Multi-Location Inventory Segmentation**: Accurately tracks, aggregates, and segregates stock across Hyderabad and Bangalore facilities.
- **Concentration-Aware Aggregation**: Strictly respects chemical concentration variations (e.g., distinguishing `1.6 M` from `2.5 M` for the same CAS number).
- **Automated Reorder Alert Engine**: Detects low stock levels against threshold requirements and generates purchase alert orders automatically.
- **Full Explainability & Auditing**: Every answer includes a step-by-step explainability trace showing how the query was parsed and filtered.

---

## 🏗️ Technical Architecture

### Technology Stack
- **Frontend / Dashboard**: [Streamlit](https://streamlit.io/)
- **Data Processing**: [Pandas](https://pandas.pydata.org/), [OpenPyXL](https://openpyxl.readthedocs.io/)
- **Entity Extraction**: Python Regular Expressions (`re`)
- **Execution Model**: Deterministic Pure Python Rule Engine (Zero LLM Hallucination Risk)

---

## 📁 Repository Structure

```text
.
├── engine.py                              # Core data processing & NLP parsing engine
├── app.py                                 # Streamlit UI dashboard application
├── Symax_AI_Stock_Assessment_100plus.xlsx # Raw inventory & minimum stock dataset
├── requirements.txt                       # Project dependencies
└── README.md                              # Technical documentation
