"""
Camara Education Ethiopia – School Infrastructure & EdTech Readiness Assessment
Script 01: Data Cleaning & Standardisation
Input:  /mnt/user-data/uploads/final_-_step_-_camara_project_schools_...xlsx
Output: outputs/cleaned_data.csv  |  outputs/cleaned_data.xlsx
"""

import pandas as pd
import numpy as np
import re
import os
os.makedirs("outputs", exist_ok=True)
os.makedirs("charts", exist_ok=True)

SRC = "input/input_data.xlsx"
OUT_CSV  = "outputs/cleaned_data.csv"
OUT_XLSX = "outputs/cleaned_data.xlsx"

# ── 1. Load ────────────────────────────────────────────────────────────────────
df = pd.read_excel(SRC, dtype=str)          # read everything as str first
df.columns = df.columns.str.strip()

# ── 2. Drop system/template columns with no analytical value ──────────────────
drop_cols = ["Intro text", "Glossary html", "School vist letter"]
df = df.drop(columns=[c for c in drop_cols if c in df.columns])

# ── 3. Strip whitespace everywhere ────────────────────────────────────────────
df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

# ── 4. Standardise region names (upper, consistent) ──────────────────────────
df["Region"] = df["Region"].str.upper().str.strip()

# ── 5. Standardise Hub Category ───────────────────────────────────────────────
hub_map = {
    "ierc": "IERC",
    "cte": "CTE",
    "ctes": "CTE",
    "aspiring female leaders": "Aspiring Female Leaders",
}
df["Hub Category"] = df["Hub Category"].str.strip().str.lower().map(
    lambda x: hub_map.get(x, x.title() if isinstance(x, str) else x)
)

# ── 6. Fix Assessor ID whitespace ─────────────────────────────────────────────
df["Assessor id"] = df["Assessor id"].str.upper().str.strip()

# ── 7. Numeric columns: coerce garbage values ─────────────────────────────────
numeric_cols = [
    "Computers teachers", "Computers students",
    "Laptops tablets teachers", "Laptops tablets students",
    "Working system units", "Non working system units",
    "Working monitors", "Non working monitors",
    "Working mice", "Non working mice",
    "Working Keyboard", "Non Working Keyboard",
    "Male teachers", "Female teachers",
    "Male Instructional", "Female Instructional",
    "Male department heads", "Female department heads",
    "Male it teachers", "Female it teachers",
    "Male non teaching", "Female non teaching",
    "Comfortable working on computer",
    "Teachers use technology for classroom instruction",
    "Participated in ongoing professional development",
    "Completed digital skills and technology integration",
    "Secure tables count", "Secure chairs count", "Working sockets count",
]
for c in numeric_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# ── 8. Standardise Yes/No boolean columns ─────────────────────────────────────
def to_bool(val):
    if pd.isna(val):
        return np.nan
    v = str(val).strip().lower()
    if v in ("yes", "true", "1", "y"):
        return "Yes"
    if v in ("no", "false", "0", "n"):
        return "No"
    return val

bool_cols = [
    "Computer lab available", "Secure room for digital learning hub",
    "Reliabel power source", "Mobile network coverage",
    "Internet in school", "Infrastructure accessible disabilities",
    "Ramps toilets signage", "Designated inclusion focal person available",
    "Willing to create technology sustainability Fund",
    "Willing to make the digital lab available for use by other schools",
    "School commitment",
]
for c in bool_cols:
    if c in df.columns:
        df[c] = df[c].apply(to_bool)

# ── 9. Clean "Average computer student ratio" (messy field) ───────────────────
def parse_ratio(val):
    if pd.isna(val):
        return np.nan
    v = str(val).strip()
    # "1:172" → 1/172
    m = re.match(r"^(\d+)[:/](\d+)$", v)
    if m:
        num, den = int(m.group(1)), int(m.group(2))
        return round(num / den, 4) if den else np.nan
    try:
        return float(v)
    except ValueError:
        return np.nan

df["Computer student ratio (numeric)"] = df["Average computer student ratio"].apply(parse_ratio)

# ── 10. Year established: coerce, flag obvious errors ─────────────────────────
df["Year established"] = pd.to_numeric(df["Year established"], errors="coerce")
df.loc[df["Year established"] > 2026, "Year established"] = np.nan   # e.g. 4988

# ── 11. Identify & flag duplicates (same School Name + Region) ────────────────
dup_mask = df.duplicated(subset=["School Name", "Region"], keep=False)
df["Duplicate flag"] = dup_mask.map({True: "DUPLICATE", False: ""})

# ── 12. Derive: total students per school (grades 1-8) ────────────────────────
male_cols   = [f"Grade {g} male"   for g in range(1, 9) if f"Grade {g} male"   in df.columns]
female_cols = [f"Grade {g} female" for g in range(1, 9) if f"Grade {g} female" in df.columns]

df[male_cols + female_cols] = df[male_cols + female_cols].apply(pd.to_numeric, errors="coerce")
df["Total students (est)"] = df[male_cols].sum(axis=1, min_count=1) + df[female_cols].sum(axis=1, min_count=1)

# ── 13. Derive: total teaching staff ──────────────────────────────────────────
df["Total teachers"] = df[["Male teachers", "Female teachers"]].apply(
    pd.to_numeric, errors="coerce"
).sum(axis=1, min_count=1)

# ── 14. Derive: power readiness score (0-3) ───────────────────────────────────
def power_score(row):
    score = 0
    if str(row.get("Reliabel power source", "")).lower() == "yes":
        score += 1
    if str(row.get("Does the current power supply reliable for DLH", "")).lower() == "yes":
        score += 1
    if str(row.get("Alternative power option", "")).lower() not in ("no alternative power available", "nan", ""):
        score += 1
    return score

df["Power readiness score (0-3)"] = df.apply(power_score, axis=1)

# ── 15. Derive: connectivity readiness score (0-3) ────────────────────────────
def conn_score(row):
    score = 0
    if str(row.get("Mobile network coverage", "")).lower() == "yes":
        score += 1
    if str(row.get("Internet in school", "")).lower() == "yes":
        score += 1
    net = str(row.get("Network reliability", "")).lower()
    if "very reliable" in net:
        score += 1
    elif "intermittent" in net:
        score += 0.5
    return score

df["Connectivity score (0-3)"] = df.apply(conn_score, axis=1)

# ── 16. Derive: infrastructure score (0-4) ────────────────────────────────────
def infra_score(row):
    score = 0
    if str(row.get("Computer lab available", "")).lower() == "yes":
        score += 1
    if str(row.get("Secure room for digital learning hub", "")).lower() == "yes":
        score += 1
    if str(row.get("Room power", "")).lower() in ("yes", "true", "1"):
        score += 1
    comp = pd.to_numeric(row.get("Computers students", 0), errors="coerce")
    if isinstance(comp, float) and comp > 0:
        score += 1
    return score

df["Infrastructure score (0-4)"] = df.apply(infra_score, axis=1)

# ── 17. Overall readiness band ────────────────────────────────────────────────
df["Total readiness score"] = (
    df["Power readiness score (0-3)"] +
    df["Connectivity score (0-3)"] +
    df["Infrastructure score (0-4)"]
)

def readiness_band(score):
    if pd.isna(score):
        return "Unknown"
    if score >= 7:
        return "High"
    if score >= 4:
        return "Medium"
    return "Low"

df["Readiness band"] = df["Total readiness score"].apply(readiness_band)

# ── 18. Save ──────────────────────────────────────────────────────────────────
df.to_csv(OUT_CSV, index=False)
df.to_excel(OUT_XLSX, index=False)

print(f"✓ Cleaned dataset saved: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"  Duplicates flagged: {(df['Duplicate flag'] == 'DUPLICATE').sum()}")
print(f"  Readiness bands:\n{df['Readiness band'].value_counts().to_string()}")
print(f"  Regions: {sorted(df['Region'].dropna().unique().tolist())}")
