"""Build a curated World Bank WDI country-year panel for Kaggle."""
from __future__ import annotations

import json
import time
from pathlib import Path

import pandas as pd
import requests

OUT = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)

# Curated high-value development indicators
INDICATORS = {
    "NY.GDP.MKTP.CD": (
        "GDP (current US$)",
        "Economy",
        "GDP at purchaser's prices in current US dollars",
    ),
    "NY.GDP.PCAP.CD": (
        "GDP per capita (current US$)",
        "Economy",
        "GDP divided by midyear population",
    ),
    "NY.GDP.MKTP.KD.ZG": (
        "GDP growth (annual %)",
        "Economy",
        "Annual percentage growth rate of GDP at market prices",
    ),
    "NY.GDP.DEFL.KD.ZG": (
        "Inflation, GDP deflator (annual %)",
        "Economy",
        "Rate of price change in the economy as a whole",
    ),
    "FP.CPI.TOTL.ZG": (
        "Inflation, consumer prices (annual %)",
        "Economy",
        "Annual % change in consumer price index",
    ),
    "NE.TRD.GNFS.ZS": (
        "Trade (% of GDP)",
        "Economy",
        "Sum of exports and imports of goods and services as % of GDP",
    ),
    "BX.KLT.DINV.WD.GD.ZS": (
        "FDI net inflows (% of GDP)",
        "Economy",
        "Foreign direct investment, net inflows as % of GDP",
    ),
    "GC.DOD.TOTL.GD.ZS": (
        "Central government debt (% of GDP)",
        "Economy",
        "Debt is the entire stock of direct government fixed-term contractual obligations",
    ),
    "SP.POP.TOTL": (
        "Population, total",
        "Demographics",
        "Total population based on de facto definition",
    ),
    "SP.POP.GROW": (
        "Population growth (annual %)",
        "Demographics",
        "Annual population growth rate",
    ),
    "SP.URB.TOTL.IN.ZS": (
        "Urban population (% of total)",
        "Demographics",
        "People living in urban areas as % of total population",
    ),
    "SP.DYN.LE00.IN": (
        "Life expectancy at birth (years)",
        "Health",
        "Number of years a newborn would live if mortality patterns stay constant",
    ),
    "SP.DYN.TFRT.IN": (
        "Fertility rate (births per woman)",
        "Health",
        "Number of children that would be born to a woman if she lived to end of childbearing years",
    ),
    "SH.DYN.MORT": (
        "Under-5 mortality rate (per 1,000)",
        "Health",
        "Probability per 1,000 that a newborn will die before age 5",
    ),
    "SH.XPD.CHEX.GD.ZS": (
        "Current health expenditure (% of GDP)",
        "Health",
        "Level of current health expenditure as % of GDP",
    ),
    "SE.ADT.LITR.ZS": (
        "Literacy rate, adult (% ages 15+)",
        "Education",
        "Percentage of people ages 15+ who can read and write",
    ),
    "SE.PRM.ENRR": (
        "School enrollment, primary (% gross)",
        "Education",
        "Ratio of total enrollment to school-age population",
    ),
    "SE.SEC.ENRR": (
        "School enrollment, secondary (% gross)",
        "Education",
        "Ratio of total enrollment to school-age population",
    ),
    "SE.TER.ENRR": (
        "School enrollment, tertiary (% gross)",
        "Education",
        "Ratio of total enrollment to school-age population",
    ),
    "SE.XPD.TOTL.GD.ZS": (
        "Government education expenditure (% of GDP)",
        "Education",
        "General government expenditure on education as % of GDP",
    ),
    "EG.USE.PCAP.KG.OE": (
        "Energy use (kg oil equiv. per capita)",
        "Energy & Environment",
        "Use of primary energy before transformation to other end-use fuels",
    ),
    "EN.ATM.CO2E.PC": (
        "CO2 emissions (metric tons per capita)",
        "Energy & Environment",
        "Carbon dioxide emissions from fossil fuels and cement",
    ),
    "EG.ELC.ACCS.ZS": (
        "Access to electricity (% of population)",
        "Energy & Environment",
        "Percentage of population with access to electricity",
    ),
    "ER.H2O.FWTL.ZS": (
        "Annual freshwater withdrawals (% of resources)",
        "Energy & Environment",
        "Total freshwater withdrawal as % of internal resources",
    ),
    "IT.NET.USER.ZS": (
        "Individuals using the Internet (% of population)",
        "Digital",
        "Internet users are individuals who have used the Internet in the last 3 months",
    ),
    "IT.CEL.SETS.P2": (
        "Mobile cellular subscriptions (per 100 people)",
        "Digital",
        "Subscriptions to a public mobile telephone service",
    ),
    "SL.UEM.TOTL.ZS": (
        "Unemployment (% of labor force)",
        "Labor",
        "Share of labor force without work but available and seeking",
    ),
    "SL.TLF.CACT.FE.ZS": (
        "Female labor force participation rate (%)",
        "Labor",
        "Proportion of female population ages 15+ that is economically active",
    ),
    "SI.POV.DDAY": (
        "Poverty headcount ratio at $2.15/day (%)",
        "Poverty & Inequality",
        "Percentage of population living below $2.15 a day (2017 PPP)",
    ),
    "SI.POV.GINI": (
        "Gini index",
        "Poverty & Inequality",
        "Gini index measures extent of inequality (0 = perfect equality)",
    ),
    "NY.GNP.PCAP.CD": (
        "GNI per capita, Atlas method (current US$)",
        "Economy",
        "GNI converted to US dollars using Atlas method, divided by midyear population",
    ),
    "NV.IND.MANF.ZS": (
        "Manufacturing value added (% of GDP)",
        "Economy",
        "Manufacturing value added as percentage of GDP",
    ),
    "AG.LND.AGRI.ZS": (
        "Agricultural land (% of land area)",
        "Agriculture",
        "Share of land area that is arable, under permanent crops, and under permanent pastures",
    ),
    "AG.PRD.FOOD.XD": (
        "Food production index (2014-2016=100)",
        "Agriculture",
        "Food production index covers food crops that are considered edible",
    ),
    "SH.H2O.SMDW.ZS": (
        "People using safely managed drinking water (%)",
        "Health",
        "Share of population using safely managed drinking water services",
    ),
    "SH.STA.BASS.ZS": (
        "People using at least basic sanitation (%)",
        "Health",
        "Share of population using at least basic sanitation services",
    ),
}

SHORT_NAMES = {
    "NY.GDP.MKTP.CD": "gdp_usd",
    "NY.GDP.PCAP.CD": "gdp_per_capita_usd",
    "NY.GDP.MKTP.KD.ZG": "gdp_growth_pct",
    "NY.GDP.DEFL.KD.ZG": "inflation_gdp_deflator_pct",
    "FP.CPI.TOTL.ZG": "inflation_cpi_pct",
    "NE.TRD.GNFS.ZS": "trade_pct_gdp",
    "BX.KLT.DINV.WD.GD.ZS": "fdi_inflows_pct_gdp",
    "GC.DOD.TOTL.GD.ZS": "gov_debt_pct_gdp",
    "SP.POP.TOTL": "population",
    "SP.POP.GROW": "population_growth_pct",
    "SP.URB.TOTL.IN.ZS": "urban_population_pct",
    "SP.DYN.LE00.IN": "life_expectancy",
    "SP.DYN.TFRT.IN": "fertility_rate",
    "SH.DYN.MORT": "under5_mortality",
    "SH.XPD.CHEX.GD.ZS": "health_exp_pct_gdp",
    "SE.ADT.LITR.ZS": "literacy_adult_pct",
    "SE.PRM.ENRR": "enrollment_primary_pct",
    "SE.SEC.ENRR": "enrollment_secondary_pct",
    "SE.TER.ENRR": "enrollment_tertiary_pct",
    "SE.XPD.TOTL.GD.ZS": "education_exp_pct_gdp",
    "EG.USE.PCAP.KG.OE": "energy_use_per_capita",
    "EN.ATM.CO2E.PC": "co2_per_capita",
    "EG.ELC.ACCS.ZS": "electricity_access_pct",
    "ER.H2O.FWTL.ZS": "freshwater_withdrawal_pct",
    "IT.NET.USER.ZS": "internet_users_pct",
    "IT.CEL.SETS.P2": "mobile_subscriptions_per_100",
    "SL.UEM.TOTL.ZS": "unemployment_pct",
    "SL.TLF.CACT.FE.ZS": "female_labor_participation_pct",
    "SI.POV.DDAY": "poverty_215_pct",
    "SI.POV.GINI": "gini_index",
    "NY.GNP.PCAP.CD": "gni_per_capita_usd",
    "NV.IND.MANF.ZS": "manufacturing_pct_gdp",
    "AG.LND.AGRI.ZS": "agricultural_land_pct",
    "AG.PRD.FOOD.XD": "food_production_index",
    "SH.H2O.SMDW.ZS": "safe_drinking_water_pct",
    "SH.STA.BASS.ZS": "basic_sanitation_pct",
}

DATE_RANGE = "2000:2024"
BASE = "https://api.worldbank.org/v2"


def fetch_json(session: requests.Session, url: str, params: dict | None = None) -> list:
    for attempt in range(5):
        try:
            resp = session.get(url, params=params, timeout=90)
            if resp.status_code == 429:
                time.sleep(2**attempt)
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception:
            if attempt == 4:
                raise
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}")


def main() -> None:
    session = requests.Session()
    session.headers.update(
        {"User-Agent": "kaggle-dataset-builder/1.0 (research; open-data)"}
    )

    print("Fetching countries...")
    payload = fetch_json(
        session, f"{BASE}/country", {"format": "json", "per_page": 500}
    )
    countries_raw = payload[1]
    countries = pd.DataFrame(
        [
            {
                "country_id": c.get("id"),
                "iso2": c.get("iso2Code"),
                "country": c.get("name"),
                "region_id": (c.get("region") or {}).get("id"),
                "region": (c.get("region") or {}).get("value"),
                "income_level_id": (c.get("incomeLevel") or {}).get("id"),
                "income_level": (c.get("incomeLevel") or {}).get("value"),
                "lending_type_id": (c.get("lendingType") or {}).get("id"),
                "lending_type": (c.get("lendingType") or {}).get("value"),
                "capital_city": c.get("capitalCity"),
                "longitude": c.get("longitude"),
                "latitude": c.get("latitude"),
            }
            for c in countries_raw
        ]
    )
    countries["is_aggregate"] = countries["region_id"].eq("NA") | countries[
        "region"
    ].eq("Aggregates")
    countries.to_csv(OUT / "countries.csv", index=False)
    print(
        f"  countries: {len(countries)} "
        f"({int(countries['is_aggregate'].sum())} aggregates)"
    )

    indicator_meta = []
    all_rows: list[dict] = []

    for i, (code, (name, category, desc)) in enumerate(INDICATORS.items(), 1):
        print(f"[{i}/{len(INDICATORS)}] {code} ...", flush=True)
        page = 1
        pages = 1
        while page <= pages:
            url = f"{BASE}/country/all/indicator/{code}"
            params = {
                "format": "json",
                "per_page": 20000,
                "date": DATE_RANGE,
                "page": page,
            }
            payload = fetch_json(session, url, params)
            meta = payload[0] if payload else {}
            pages = int(meta.get("pages") or 1)
            data = payload[1] if len(payload) > 1 else []
            if not data:
                break
            for d in data:
                country = d.get("country") or {}
                all_rows.append(
                    {
                        "country_id": d.get("countryiso3code") or country.get("id"),
                        "country": country.get("value"),
                        "indicator_code": code,
                        "indicator_name": name,
                        "category": category,
                        "year": int(d["date"]) if d.get("date") else None,
                        "value": d.get("value"),
                    }
                )
            page += 1
            time.sleep(0.12)

        indicator_meta.append(
            {
                "indicator_code": code,
                "indicator_name": name,
                "category": category,
                "description": desc,
                "column_name_wide": SHORT_NAMES[code],
                "source": "World Bank World Development Indicators (WDI)",
                "api_endpoint": f"{BASE}/country/all/indicator/{code}",
                "year_start": 2000,
                "year_end": 2024,
            }
        )
        time.sleep(0.2)

    long_df = pd.DataFrame(all_rows)
    long_df = long_df[
        long_df["country_id"].notna()
        & (long_df["country_id"].astype(str).str.len() > 0)
    ]
    long_df = long_df.sort_values(
        ["country_id", "indicator_code", "year"]
    ).reset_index(drop=True)

    meta_cols = ["country_id", "iso2", "region", "income_level", "is_aggregate"]
    long_enriched = long_df.merge(countries[meta_cols], on="country_id", how="left")

    country_only = long_enriched[~long_enriched["is_aggregate"].fillna(False)].copy()
    country_vals = country_only[country_only["value"].notna()].copy()

    wide = (
        country_vals.pivot_table(
            index=[
                "country_id",
                "country",
                "iso2",
                "region",
                "income_level",
                "year",
            ],
            columns="indicator_code",
            values="value",
            aggfunc="first",
        )
        .reset_index()
    )
    wide.columns.name = None
    wide = wide.rename(columns={c: SHORT_NAMES[c] for c in wide.columns if c in SHORT_NAMES})

    long_out = country_vals[
        [
            "country_id",
            "country",
            "iso2",
            "region",
            "income_level",
            "indicator_code",
            "indicator_name",
            "category",
            "year",
            "value",
        ]
    ].sort_values(["country", "indicator_code", "year"]).reset_index(drop=True)

    agg_vals = long_enriched[
        long_enriched["is_aggregate"].fillna(False) & long_enriched["value"].notna()
    ].copy()
    agg_out = agg_vals[
        [
            "country_id",
            "country",
            "region",
            "income_level",
            "indicator_code",
            "indicator_name",
            "category",
            "year",
            "value",
        ]
    ].sort_values(["country", "indicator_code", "year"]).reset_index(drop=True)

    ind_df = pd.DataFrame(indicator_meta)
    coverage = (
        long_out.groupby(["indicator_code", "indicator_name"])
        .agg(
            non_null_rows=("value", "count"),
            countries=("country_id", "nunique"),
            year_min=("year", "min"),
            year_max=("year", "max"),
        )
        .reset_index()
        .sort_values("non_null_rows", ascending=False)
    )

    long_out.to_csv(OUT / "wdi_country_indicators_long.csv", index=False)
    wide.to_csv(OUT / "wdi_country_year_panel.csv", index=False)
    agg_out.to_csv(OUT / "wdi_aggregates_long.csv", index=False)
    ind_df.to_csv(OUT / "indicator_dictionary.csv", index=False)
    coverage.to_csv(OUT / "data_coverage_summary.csv", index=False)

    summary = {
        "n_countries_panel": int(wide["country_id"].nunique()),
        "n_years": int(wide["year"].nunique()),
        "year_min": int(wide["year"].min()),
        "year_max": int(wide["year"].max()),
        "n_indicators": len(INDICATORS),
        "panel_rows": int(len(wide)),
        "long_rows": int(len(long_out)),
        "aggregate_rows": int(len(agg_out)),
        "panel_cols": list(wide.columns),
    }
    (OUT / "build_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    print("Done ->", OUT)


if __name__ == "__main__":
    main()
