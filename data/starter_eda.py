"""
Starter EDA for World Bank Development Indicators Panel
Upload this as a Kaggle notebook after publishing the dataset.
Path on Kaggle: /kaggle/input/world-bank-development-indicators-panel/
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Local path when running on your machine; Kaggle path when on the site
LOCAL = Path(__file__).resolve().parent
KAGGLE = Path("/kaggle/input/world-bank-development-indicators-panel")
DATA = KAGGLE if KAGGLE.exists() else LOCAL

sns.set_theme(style="whitegrid", context="notebook")

panel = pd.read_csv(DATA / "wdi_country_year_panel.csv")
dictionary = pd.read_csv(DATA / "indicator_dictionary.csv")
coverage = pd.read_csv(DATA / "data_coverage_summary.csv")

print("Panel shape:", panel.shape)
print("Years:", panel["year"].min(), "–", panel["year"].max())
print("Countries:", panel["country_id"].nunique())
print("\nCoverage (top indicators):")
print(coverage.head(10).to_string(index=False))

# Latest complete-ish year for cross-section
year = int(panel["year"].max())
snap = panel[panel["year"] == year].copy()
print(f"\nCross-section year: {year} | rows: {len(snap)}")

# 1) GDP per capita vs life expectancy
fig, ax = plt.subplots(figsize=(9, 6))
plot_df = snap.dropna(subset=["gdp_per_capita_usd", "life_expectancy"])
sns.scatterplot(
    data=plot_df,
    x="gdp_per_capita_usd",
    y="life_expectancy",
    hue="region",
    ax=ax,
    alpha=0.85,
)
ax.set_xscale("log")
ax.set_title(f"Life expectancy vs GDP per capita ({year})")
ax.set_xlabel("GDP per capita (US$, log scale)")
ax.set_ylabel("Life expectancy (years)")
ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
plt.tight_layout()
plt.show()

# 2) Internet adoption over time by income group
trend = (
    panel.dropna(subset=["internet_users_pct"])
    .groupby(["year", "income_level"], as_index=False)["internet_users_pct"]
    .mean()
)
fig, ax = plt.subplots(figsize=(9, 5))
sns.lineplot(
    data=trend,
    x="year",
    y="internet_users_pct",
    hue="income_level",
    marker="o",
    ax=ax,
)
ax.set_title("Mean internet users (% of population) by income group")
ax.set_ylabel("Internet users (%)")
ax.legend(title="Income level", fontsize=8)
plt.tight_layout()
plt.show()

# 3) Top 15 countries by GDP per capita (latest year)
top = (
    snap.dropna(subset=["gdp_per_capita_usd"])
    .nlargest(15, "gdp_per_capita_usd")
    [["country", "region", "gdp_per_capita_usd", "life_expectancy", "internet_users_pct"]]
)
print("\nTop 15 GDP per capita:")
print(top.to_string(index=False))

# 4) Correlation heatmap of selected development pillars
cols = [
    "gdp_per_capita_usd",
    "life_expectancy",
    "under5_mortality",
    "internet_users_pct",
    "electricity_access_pct",
    "unemployment_pct",
    "female_labor_participation_pct",
    "co2_per_capita",
]
corr = snap[cols].corr(numeric_only=True)
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax)
ax.set_title(f"Development pillar correlations ({year})")
plt.tight_layout()
plt.show()

print("\nDone. Fork this notebook and dig into poverty, education, or climate next.")
