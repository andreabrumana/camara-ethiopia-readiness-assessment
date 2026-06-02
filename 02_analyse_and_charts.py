"""
Camara Education Ethiopia – School Infrastructure & EdTech Readiness Assessment
Script 02: Analysis & Chart Generation
Input:  outputs/cleaned_data.csv
Output: charts/*.png  |  outputs/analytical_summary.xlsx
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv("outputs/cleaned_data.csv", low_memory=False)

# ── Colour palette (Camara blue / UNICEF cyan family) ─────────────────────────
C_BLUE   = "#1A5276"
C_CYAN   = "#00AEEF"
C_GREEN  = "#27AE60"
C_ORANGE = "#E67E22"
C_RED    = "#C0392B"
C_GREY   = "#BDC3C7"
PALETTE  = [C_BLUE, C_CYAN, C_GREEN, C_ORANGE, C_RED, "#7D3C98", "#117A65"]

def save(fig, name):
    fig.savefig(f"charts/{name}.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓ charts/{name}.png")

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 1 – Schools by Region & Hub Category (grouped bar)
# ═══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 5))
cross = pd.crosstab(df["Region"], df["Hub Category"])
cross.plot(kind="bar", ax=ax, color=[C_BLUE, C_CYAN, C_GREEN], edgecolor="white", width=0.7)
ax.set_title("Schools Assessed by Region and Hub Category", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("")
ax.set_ylabel("Number of Schools")
ax.tick_params(axis="x", rotation=30)
ax.legend(title="Hub Category", frameon=False)
ax.spines[["top", "right"]].set_visible(False)
for container in ax.containers:
    ax.bar_label(container, fmt="%d", fontsize=8, padding=2)
save(fig, "fig1_schools_by_region_hub")

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 2 – Overall Readiness Band Distribution (donut)
# ═══════════════════════════════════════════════════════════════════════════════
bands = df["Readiness band"].value_counts()
colours_band = {"High": C_GREEN, "Medium": C_ORANGE, "Low": C_RED, "Unknown": C_GREY}
fig, ax = plt.subplots(figsize=(7, 6))
wedges, texts, autotexts = ax.pie(
    bands.values,
    labels=bands.index,
    autopct="%1.0f%%",
    colors=[colours_band.get(b, C_GREY) for b in bands.index],
    startangle=90,
    pctdistance=0.75,
    wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
)
for t in autotexts:
    t.set_fontsize(12); t.set_fontweight("bold")
ax.set_title("Overall Digital Readiness Bands\n(Power + Connectivity + Infrastructure)",
             fontsize=13, fontweight="bold", pad=16)
centre = ax.text(0, 0, f"{len(df)}\nSchools", ha="center", va="center",
                 fontsize=14, fontweight="bold", color=C_BLUE)
save(fig, "fig2_readiness_band_donut")

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 3 – Readiness Scores by Region (stacked bar)
# ═══════════════════════════════════════════════════════════════════════════════
score_cols = ["Power readiness score (0-3)", "Connectivity score (0-3)", "Infrastructure score (0-4)"]
score_labels = ["Power (max 3)", "Connectivity (max 3)", "Infrastructure (max 4)"]
region_scores = df.groupby("Region")[score_cols].mean().round(2)

fig, ax = plt.subplots(figsize=(11, 5))
bottom = np.zeros(len(region_scores))
colours_stacked = [C_ORANGE, C_CYAN, C_BLUE]
for col, label, colour in zip(score_cols, score_labels, colours_stacked):
    vals = region_scores[col].values
    bars = ax.bar(region_scores.index, vals, bottom=bottom, label=label,
                  color=colour, edgecolor="white", linewidth=0.8)
    for bar, val, bot in zip(bars, vals, bottom):
        if val > 0.2:
            ax.text(bar.get_x() + bar.get_width()/2, bot + val/2,
                    f"{val:.1f}", ha="center", va="center", fontsize=8,
                    color="white", fontweight="bold")
    bottom += vals

ax.set_title("Average Readiness Scores by Region", fontsize=14, fontweight="bold", pad=12)
ax.set_ylabel("Average Score")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=25)
ax.legend(frameon=False, loc="upper right")
ax.spines[["top", "right"]].set_visible(False)
ax.axhline(y=7, color="red", linestyle="--", linewidth=1, alpha=0.5, label="High threshold (7)")
save(fig, "fig3_readiness_by_region_stacked")

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 4 – Power Supply Overview (horizontal bars)
# ═══════════════════════════════════════════════════════════════════════════════
power_q = {
    "Has electricity": (df["Reliabel power source"] == "Yes").sum(),
    "Power reliable for Digital Hub": (df["Does the current power supply reliable for DLH"] == "Yes").sum(),
    "Has backup/alternative power": (~df["Alternative power option"].isin(
        ["No alternative power available", np.nan]
    ) & df["Alternative power option"].notna()).sum(),
    "Frequent outages (≥weekly)": df["Frequency and duration of power outages"].str.contains(
        "Frequent|Prolonged", na=False, case=False).sum(),
}
fig, ax = plt.subplots(figsize=(9, 4))
keys = list(power_q.keys())
vals = list(power_q.values())
colours_h = [C_GREEN if v >= 20 else C_ORANGE if v >= 10 else C_RED for v in vals]
bars = ax.barh(keys, vals, color=colours_h, edgecolor="white")
ax.bar_label(bars, fmt="%d", padding=4, fontsize=11, fontweight="bold")
ax.set_xlim(0, len(df) + 4)
ax.axvline(x=len(df), color=C_GREY, linestyle="--", linewidth=1)
ax.set_title("Power Supply Readiness (n=34 schools)", fontsize=13, fontweight="bold", pad=12)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(left=False)
save(fig, "fig4_power_readiness")

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 5 – Internet & Mobile Connectivity
# ═══════════════════════════════════════════════════════════════════════════════
conn_q = {
    "Mobile network present": (df["Mobile network coverage"].str.lower() == "yes").sum(),
    "Internet in school": (df["Internet in school"].str.lower() == "yes").sum(),
    "Internet adequate for learning": df["Internet speed for DLC"].str.contains("Adequate", na=False).sum(),
    "Fiber connection": df["Internet in school type"].str.contains("Fiber", na=False).sum(),
}
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Left: horizontal bar
ax = axes[0]
keys = list(conn_q.keys())
vals = list(conn_q.values())
col_h = [C_GREEN if v >= 25 else C_ORANGE if v >= 10 else C_RED for v in vals]
bars = ax.barh(keys, vals, color=col_h, edgecolor="white")
ax.bar_label(bars, fmt="%d / 34", padding=4, fontsize=10, fontweight="bold")
ax.set_xlim(0, 42)
ax.set_title("Connectivity Indicators", fontsize=12, fontweight="bold")
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(left=False)

# Right: mobile network type breakdown
ax2 = axes[1]
net_type = df["Mobile network coverage type"].dropna()
# Explode multi-select
net_flat = []
for v in net_type:
    for part in str(v).split(","):
        p = part.strip()
        if p:
            net_flat.append(p)
net_series = pd.Series(net_flat).value_counts().head(6)
net_series.plot(kind="bar", ax=ax2, color=PALETTE[:len(net_series)], edgecolor="white")
ax2.set_title("Mobile Network Types Available", fontsize=12, fontweight="bold")
ax2.set_ylabel("# of Schools")
ax2.tick_params(axis="x", rotation=20)
ax2.spines[["top", "right"]].set_visible(False)
for bar in ax2.patches:
    ax2.annotate(f"{int(bar.get_height())}", (bar.get_x() + bar.get_width()/2, bar.get_height()),
                 ha="center", va="bottom", fontsize=10, fontweight="bold")

fig.suptitle("Internet & Mobile Connectivity Overview", fontsize=14, fontweight="bold", y=1.01)
fig.tight_layout()
save(fig, "fig5_connectivity")

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 6 – ICT Equipment & Computer Labs
# ═══════════════════════════════════════════════════════════════════════════════
lab_yes = (df["Computer lab available"] == "Yes").sum()
lab_no  = (df["Computer lab available"] == "No").sum()
room_yes = (df["Secure room for digital learning hub"] == "Yes").sum()

total_working = pd.to_numeric(df["Working system units"], errors="coerce").sum()
total_broken  = pd.to_numeric(df["Non working system units"], errors="coerce").sum()
comp_teach    = pd.to_numeric(df["Computers teachers"], errors="coerce").sum()
comp_stud     = pd.to_numeric(df["Computers students"], errors="coerce").sum()

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Left: lab availability pie
ax = axes[0]
ax.pie([lab_yes, lab_no], labels=["Has Computer Lab", "No Computer Lab"],
       colors=[C_BLUE, C_GREY], autopct="%1.0f%%", startangle=90,
       wedgeprops=dict(edgecolor="white", linewidth=2))
ax.set_title("Existing Computer Lab Availability", fontsize=12, fontweight="bold")

# Right: equipment counts
ax2 = axes[1]
labels = ["Working\nComputers", "Non-working\nComputers", "Computers\nfor Teachers", "Computers\nfor Students"]
values = [total_working, total_broken, comp_teach, comp_stud]
colours_eq = [C_GREEN, C_RED, C_BLUE, C_CYAN]
bars = ax2.bar(labels, values, color=colours_eq, edgecolor="white", width=0.6)
ax2.bar_label(bars, fmt="%d", padding=3, fontsize=11, fontweight="bold")
ax2.set_title("ICT Equipment Inventory\n(All schools combined)", fontsize=12, fontweight="bold")
ax2.spines[["top", "right"]].set_visible(False)
ax2.set_ylabel("Units")

# Add annotation for secure room
ax2.text(0.98, 0.95, f"{room_yes}/34 schools\nhave a secure room\nfor a Digital Hub",
         transform=ax2.transAxes, ha="right", va="top", fontsize=9,
         bbox=dict(boxstyle="round,pad=0.4", facecolor=C_CYAN, alpha=0.2))

fig.suptitle("ICT Equipment & Infrastructure", fontsize=14, fontweight="bold")
fig.tight_layout()
save(fig, "fig6_ict_equipment")

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 7 – Teacher Digital Capacity
# ═══════════════════════════════════════════════════════════════════════════════
teach_metrics = {
    "Completed digital\ntraining (past yr)": pd.to_numeric(df["Completed digital skills and technology integration"], errors="coerce").sum(),
    "Comfortable using\na computer": pd.to_numeric(df["Comfortable working on computer"], errors="coerce").sum(),
    "Using tech in\nclassroom": pd.to_numeric(df["Teachers use technology for classroom instruction"], errors="coerce").sum(),
    "Total teachers\n(all schools)": pd.to_numeric(df[["Male teachers","Female teachers"]].apply(pd.to_numeric, errors="coerce").sum(axis=1), errors="coerce").sum(),
}

fig, ax = plt.subplots(figsize=(10, 4))
keys = list(teach_metrics.keys())
vals = list(teach_metrics.values())
colours_t = [C_CYAN, C_BLUE, C_GREEN, C_GREY]
bars = ax.bar(keys, vals, color=colours_t, edgecolor="white", width=0.55)
ax.bar_label(bars, fmt="%d", padding=3, fontsize=12, fontweight="bold")

# Percentage overlays (of total teachers)
total_t = vals[-1] if vals[-1] > 0 else 1
for i, (bar, val) in enumerate(zip(bars[:-1], vals[:-1])):
    pct = val / total_t * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(vals)*0.03,
            f"({pct:.0f}%)", ha="center", va="bottom", fontsize=9, color="#555")

ax.set_title("Teacher Digital Capacity Indicators", fontsize=14, fontweight="bold", pad=12)
ax.set_ylabel("Number of Teachers")
ax.spines[["top", "right"]].set_visible(False)
save(fig, "fig7_teacher_capacity")

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 8 – Inclusion & Accessibility
# ═══════════════════════════════════════════════════════════════════════════════
incl_q = {
    "Infra accessible\nto PWDs": (df["Infrastructure accessible disabilities"] == "Yes").sum(),
    "Ramps/toilets/\nsignage present": (df["Ramps toilets signage"] == "Yes").sum(),
    "Inclusion focal\nperson assigned": (df["Designated inclusion focal person available"] == "Yes").sum(),
}

disability_cols_m = ["Visual male", "Hearing male", "Physical male", "Developmental male"]
disability_cols_f = ["Visual female", "Hearing female", "Physical female", "Developmental female"]
dis_labels = ["Visual", "Hearing", "Physical", "Developmental"]
dis_male   = [pd.to_numeric(df[c], errors="coerce").sum() for c in disability_cols_m]
dis_female = [pd.to_numeric(df[c], errors="coerce").sum() for c in disability_cols_f]

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

ax = axes[0]
x = np.arange(len(incl_q))
bars = ax.bar(x, list(incl_q.values()), color=[C_BLUE, C_CYAN, C_GREEN], edgecolor="white", width=0.5)
ax.set_xticks(x); ax.set_xticklabels(list(incl_q.keys()), fontsize=10)
ax.bar_label(bars, fmt="%d", padding=3, fontsize=12, fontweight="bold")
ax.axhline(y=34, color=C_GREY, linestyle="--", linewidth=1, alpha=0.7)
ax.set_title("Accessibility & Inclusion Infrastructure", fontsize=12, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
ax.set_ylabel("# of Schools")

ax2 = axes[1]
x2 = np.arange(len(dis_labels))
w = 0.35
b1 = ax2.bar(x2 - w/2, dis_male,   width=w, label="Male",   color=C_BLUE,  edgecolor="white")
b2 = ax2.bar(x2 + w/2, dis_female, width=w, label="Female", color=C_CYAN, edgecolor="white")
ax2.set_xticks(x2); ax2.set_xticklabels(dis_labels)
ax2.bar_label(b1, fmt="%d", fontsize=8, padding=2)
ax2.bar_label(b2, fmt="%d", fontsize=8, padding=2)
ax2.set_title("Students with Disabilities by Type & Gender", fontsize=12, fontweight="bold")
ax2.legend(frameon=False)
ax2.spines[["top", "right"]].set_visible(False)
ax2.set_ylabel("Number of Students")

fig.suptitle("Inclusion & Accessibility", fontsize=14, fontweight="bold")
fig.tight_layout()
save(fig, "fig8_inclusion")

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 9 – Sustainability & Community Engagement
# ═══════════════════════════════════════════════════════════════════════════════
sust_q = {
    "Willing to create\nTech Sustainability Fund": (df["Willing to create technology sustainability Fund"] == "Yes").sum(),
    "Willing to share\nDigital Hub with others": (df["Willing to make the digital lab available for use by other schools"] == "Yes").sum(),
    "School shows commitment\nto initiative": (df["School commitment"] == "Yes").sum(),
    "Existing EdTech\npartnership/initiative": (df["Existing partnerships with others"] == "Yes").sum(),
}

fig, ax = plt.subplots(figsize=(10, 4))
keys = list(sust_q.keys())
vals = list(sust_q.values())
cols = [C_GREEN if v >= 25 else C_ORANGE if v >= 15 else C_RED for v in vals]
bars = ax.bar(keys, vals, color=cols, edgecolor="white", width=0.55)
ax.bar_label(bars, fmt="%d / 34", padding=3, fontsize=11, fontweight="bold")
ax.set_title("Sustainability & Community Engagement", fontsize=14, fontweight="bold", pad=12)
ax.set_ylabel("# of Schools")
ax.set_ylim(0, 40)
ax.spines[["top", "right"]].set_visible(False)
save(fig, "fig9_sustainability")

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 10 – School Profile Summary Heatmap (readiness by school)
# ═══════════════════════════════════════════════════════════════════════════════
import matplotlib.colors as mcolors

heatmap_cols = [
    "Power readiness score (0-3)",
    "Connectivity score (0-3)",
    "Infrastructure score (0-4)",
]
hm_df = df[["School Name", "Region"] + heatmap_cols].copy()
hm_df = hm_df.dropna(subset=heatmap_cols)
hm_df["School Name"] = hm_df["School Name"].str[:35]  # truncate long names
hm_df = hm_df.sort_values("Region")

fig, ax = plt.subplots(figsize=(10, max(8, len(hm_df) * 0.35)))

data_matrix = hm_df[heatmap_cols].values.astype(float)
max_scores = [3, 3, 4]
norm_matrix = data_matrix / max_scores  # normalise to 0-1

cmap = matplotlib.colormaps["RdYlGn"]
im = ax.imshow(norm_matrix, cmap=cmap, aspect="auto", vmin=0, vmax=1)

ax.set_xticks(range(len(heatmap_cols)))
ax.set_xticklabels(["Power\n(0-3)", "Connectivity\n(0-3)", "Infrastructure\n(0-4)"], fontsize=10, fontweight="bold")
ax.set_yticks(range(len(hm_df)))
ax.set_yticklabels(
    [f"{row['School Name']} ({row['Region'][:3]})" for _, row in hm_df.iterrows()],
    fontsize=8
)

for i in range(len(hm_df)):
    for j in range(len(heatmap_cols)):
        val = data_matrix[i, j]
        ax.text(j, i, f"{val:.0f}", ha="center", va="center",
                fontsize=9, fontweight="bold",
                color="black" if norm_matrix[i, j] > 0.4 else "white")

plt.colorbar(im, ax=ax, fraction=0.02, pad=0.04, label="Normalised Score")
ax.set_title("Readiness Score Heatmap by School", fontsize=13, fontweight="bold", pad=12)
fig.tight_layout()
save(fig, "fig10_heatmap_by_school")

print("\nAll charts generated.")

# ═══════════════════════════════════════════════════════════════════════════════
# ANALYTICAL SUMMARY – Excel workbook
# ═══════════════════════════════════════════════════════════════════════════════
print("\nBuilding analytical summary workbook …")
with pd.ExcelWriter("outputs/analytical_summary.xlsx", engine="openpyxl") as writer:

    # Sheet 1: Overview stats
    overview = pd.DataFrame({
        "Metric": [
            "Total schools assessed",
            "Regions covered",
            "Hub categories",
            "Schools: High readiness",
            "Schools: Medium readiness",
            "Schools: Low readiness",
            "Schools with Computer Lab",
            "Schools with secure room for Digital Hub",
            "Schools with electricity",
            "Schools with internet",
            "Schools with mobile coverage",
            "Total students (estimated)",
            "Total teachers",
        ],
        "Value": [
            len(df),
            df["Region"].nunique(),
            df["Hub Category"].nunique(),
            (df["Readiness band"] == "High").sum(),
            (df["Readiness band"] == "Medium").sum(),
            (df["Readiness band"] == "Low").sum(),
            (df["Computer lab available"] == "Yes").sum(),
            (df["Secure room for digital learning hub"] == "Yes").sum(),
            (df["Reliabel power source"] == "Yes").sum(),
            (df["Internet in school"].str.lower() == "yes").sum(),
            (df["Mobile network coverage"].str.lower() == "yes").sum(),
            int(pd.to_numeric(df["Total students (est)"], errors="coerce").sum()),
            int(pd.to_numeric(df["Total teachers"], errors="coerce").sum()),
        ]
    })
    overview.to_excel(writer, sheet_name="Overview", index=False)

    # Sheet 2: By Region
    region_summary = df.groupby("Region").agg(
        Schools=("ID", "count"),
        High_readiness=("Readiness band", lambda x: (x == "High").sum()),
        Medium_readiness=("Readiness band", lambda x: (x == "Medium").sum()),
        Low_readiness=("Readiness band", lambda x: (x == "Low").sum()),
        Avg_power_score=("Power readiness score (0-3)", "mean"),
        Avg_connectivity_score=("Connectivity score (0-3)", "mean"),
        Avg_infrastructure_score=("Infrastructure score (0-4)", "mean"),
        Avg_total_score=("Total readiness score", "mean"),
        Has_internet=("Internet in school", lambda x: (x.str.lower() == "yes").sum()),
        Has_computer_lab=("Computer lab available", lambda x: (x == "Yes").sum()),
    ).round(2).reset_index()
    region_summary.to_excel(writer, sheet_name="By Region", index=False)

    # Sheet 3: By Hub Category
    hub_summary = df.groupby("Hub Category").agg(
        Schools=("ID", "count"),
        High_readiness=("Readiness band", lambda x: (x == "High").sum()),
        Medium_readiness=("Readiness band", lambda x: (x == "Medium").sum()),
        Low_readiness=("Readiness band", lambda x: (x == "Low").sum()),
        Avg_total_score=("Total readiness score", "mean"),
    ).round(2).reset_index()
    hub_summary.to_excel(writer, sheet_name="By Hub Category", index=False)

    # Sheet 4: School-level readiness matrix
    school_matrix = df[[
        "School Name", "Region", "Hub Category", "School level type",
        "Power readiness score (0-3)", "Connectivity score (0-3)",
        "Infrastructure score (0-4)", "Total readiness score", "Readiness band",
        "Computer lab available", "Secure room for digital learning hub",
        "Reliabel power source", "Internet in school",
        "Total students (est)", "Total teachers", "Duplicate flag"
    ]].sort_values(["Region", "Total readiness score"], ascending=[True, False])
    school_matrix.to_excel(writer, sheet_name="School Readiness Matrix", index=False)

    # Sheet 5: Data quality log
    quality_log = pd.DataFrame({
        "Issue": [
            "Duplicate school entries (same name + region)",
            "Missing 'Year established' (invalid values removed)",
            "Inconsistent computer-student ratio format",
            "Schools with all enrollment data missing",
        ],
        "Count": [
            (df["Duplicate flag"] == "DUPLICATE").sum(),
            df["Year established"].isna().sum(),
            df["Average computer student ratio"].notna().sum(),
            (df["Total students (est)"] == 0).sum(),
        ],
        "Action taken": [
            "Flagged in 'Duplicate flag' column; both records retained",
            "Coerced to NaN (e.g. year 4988 removed)",
            "Parsed to numeric in 'Computer student ratio (numeric)' column",
            "Retained; likely CTEs/institutions without grade-level data",
        ]
    })
    quality_log.to_excel(writer, sheet_name="Data Quality Log", index=False)

print("✓ outputs/analytical_summary.xlsx")
print("\nDone.")
