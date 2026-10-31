# World Bank Development Indicators Panel (2000–2024)

Clean, analysis-ready **country–year panel** from World Bank WDI open data.

## Files

| File | Role |
|------|------|
| `wdi_country_year_panel.csv` | Main wide panel |
| `wdi_country_indicators_long.csv` | Long/tidy format |
| `wdi_aggregates_long.csv` | Regional / income aggregates |
| `countries.csv` | Country metadata |
| `indicator_dictionary.csv` | Indicator codebook |
| `data_coverage_summary.csv` | Coverage stats |
| `build_dataset.py` | Rebuild from API |
| `dataset-metadata.json` | Kaggle upload metadata |

## Stats

- 217 countries
- Years 2000–2024
- 36 curated indicators
- ~5,425 panel rows

## Publish to Kaggle

1. Get API token: https://www.kaggle.com/settings → **Create New Token** → save as `%USERPROFILE%\.kaggle\kaggle.json`
2. Edit `dataset-metadata.json`: replace `YOUR_USERNAME` with your Kaggle username
3. From this folder:

```powershell
cd C:\Users\madhu\kaggle-datasets\world-bank-development-indicators
kaggle datasets create -p . --dir-mode zip
```

To update later:

```powershell
kaggle datasets version -p . -m "Refresh WDI pull" --dir-mode zip
```

## Rebuild data

```powershell
python build_dataset.py
```

## License

CC BY 4.0 — World Bank Open Data (attribution required).
