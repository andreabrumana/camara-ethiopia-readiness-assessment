# Camara Education Ethiopia – Schools Infrastructure & EdTech Readiness Assessment

Analysis scripts developed as part of the UNV Online Volunteering assignment for **Camara Education Ethiopia / UNICEF Ethiopia**, supporting the programme *"Digital and Transferable Skills Development: Transforming in-School Learning and Transition to Earning"* (April 2026 – December 2027).

---

## Context

As part of programme start-up, Camara conducted a **Schools Infrastructure and Technology Readiness Assessment** across 115 institutions in Ethiopia. The assessment covers infrastructure, ICT equipment, connectivity, power reliability, teacher capacity, and inclusion indicators.

This repository contains the scripts used to clean, analyse, and visualise the collected data, producing outputs for reporting to UNICEF, the Ministry of Education (MoE), Regional Education Bureaus (REBs), and donors.

---

## Repository Structure

```
├── 01_clean_data.py          # Data cleaning and standardisation
├── 02_analyse_and_charts.py  # Analysis, scoring, and chart generation
├── README.md
│
├── input/                    # Raw data files (not tracked - contains personal data)
├── outputs/                  # Cleaned dataset and analytical summary (not tracked)
└── charts/                   # Generated chart PNGs (not tracked)
```

---

## Outputs

Running the scripts produces:

| Output | Description |
|---|---|
| `outputs/cleaned_data.csv` | Cleaned dataset, ready for Looker Studio / Power BI |
| `outputs/cleaned_data.xlsx` | Same, in Excel format |
| `outputs/analytical_summary.xlsx` | 5-sheet workbook: KPIs, by-region, by-hub, school matrix, data quality log |
| `charts/fig1_*.png … fig10_*.png` | 10 charts covering readiness, power, connectivity, ICT, inclusion, sustainability |

---

## Setup

**Requirements:** Python 3.10+

```bash
# Clone the repo
git clone https://github.com/andreabrumana/camara-ethiopia-readiness-assessment.git
cd camara-ethiopia-readiness-assessment

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install pandas openpyxl matplotlib seaborn xlsxwriter
```

---

## Usage

Place the raw assessment `.xlsx` file in the `input/` folder, then update the `SRC` path at the top of `01_clean_data.py` to match the filename.

```bash
# Step 1 – clean the data
python3 01_clean_data.py

# Step 2 – run analysis and generate charts
python3 02_analyse_and_charts.py
```

To update when new data arrives (e.g. MCF and OF schools), replace the source file and re-run both scripts in order.

---

## Readiness Scoring

Each school receives a **Total Readiness Score (0–10)** composed of three dimensions:

| Dimension | Max | Criteria |
|---|---|---|
| Power | 3 | Electricity present (+1), reliable for Digital Hub (+1), backup power available (+1) |
| Connectivity | 3 | Mobile coverage (+1), internet on-site (+1), reliable network (+1) |
| Infrastructure | 4 | Computer lab (+1), secure room for hub (+1), power in room (+1), computers for students (+1) |

Bands: **High** ≥ 7 · **Medium** 4–6 · **Low** < 4

---

## Data Privacy

Raw data files are excluded from this repository (see `.gitignore`) as they contain personal information (school directors' names, phone numbers, and email addresses). Data files are shared exclusively through Camara's secure Google Workspace environment.

---

## Assignment

- **Programme:** Digital and Transferable Skills Development (UNICEF / Camara Education Ethiopia)
- **Role:** Data Analyst – UNV Online Volunteer
- **Supervision:** Digital Learning & AI Lead, Camara Education Ethiopia
- **Duration:** 4 weeks · Online · 2026
