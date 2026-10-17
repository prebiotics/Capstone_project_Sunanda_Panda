# Capstone_project_Sunanda_Panda

## 1. SQL analysis using SQLiteOnline

Open [SQLiteOnline](https://sqliteonline.com/) and select SQLite.

1. Open `sql/schema.sql`, copy its SQL statements into the editor, and execute them to create the tables.
2. Open `sql/seed_data.sql`, copy its statements into the editor, and execute them to load the data.
3. Open `sql/reports.sql`, execute the queries, and review the results.

Run these scripts in the same database session, in the order shown. Save or export the database if the online editor supports it.

## 2. Python analysis using Google Colab

Open [Google Colab](https://colab.research.google.com/) and create a notebook.

Upload the input data files in a new folder naming data. Keep the directory structure consistent with the repository and ensure that the CSV files required by the analysis are available in Colab.

Step1: Install the dependencies:

```python
!pip install -q pandas matplotlib google-genai
```

Run the cleaning and exploratory data analysis script:

```python
!python analysis/clean_and_eda.py
```

This script cleans the data, calculates the required metrics, and writes the verified results to `narrator/findings.json`.
Task 5 of Part 2 should produce this file from the analysis rather than relying on a manually written JSON file.

Then run the visualization script to obtain and save the charts:

```python
!python analysis/visualize.py
```

The charts are saved in the `visualizations/` directory.

## 3. Run the GenAI narrative generator

The clean_and_eda.py in the end have the code to generate and save the json file.

Run the script after `narrator/findings.json` has been generated:

```python
!python narrator/generate_narrative.py
```

The generator uses the verified findings to create a business narrative with three sections: Situation, Complication, and Resolution.

### Online Gemini mode

Obtain an API key through [Google AI Studio](https://aistudio.google.com/) and check the current free usage tier and its limits.

In Google Colab, add a secret named `GEMINI_API_KEY` using the Secrets panel and enable notebook access. Set the environment variable:

```python
import os
from google.colab import userdata

os.environ["GEMINI_API_KEY"] = userdata.get("GEMINI_API_KEY")
```

Then run the narrative generator. It attempts to generate the narrative using Gemini.

### Offline mode

Leave `GEMINI_API_KEY` unset and run:

```python
!python narrator/generate_narrative.py
```

The generator uses a deterministic Python template if no key is configured or the Gemini request fails. This path requires no API key, network access, or API spending.

## 4. Numeric accuracy verification

The generator saves its narrative to `narrator/sample_output.txt`.

The numeric accuracy checker verifies the following required figures:

- Cleaned revenue: 97,358.30
- COD return rate: 44.4%
- COD + Tier-2 return rate: 54.5%
- Duplicate-reconciliation difference: 2,501.90
- March 2026 peak revenue: 20,318.90

All five checks must print `PASS`. Inspect the saved sample output if any check fails.

## 5. End-to-end execution order

1. Execute `sql/schema.sql` in SQLiteOnline.
2. Then execute `sql/seed_data.sql`.
3. Execute `sql/reports.sql` to get the queries.
4. Upload the required data and scripts to Google Colab.
5. Run `analysis/clean_and_eda.py` to generate `narrator/findings.json`.
6. Run `analysis/visualize.py` to create the charts.
7. Run `narrator/generate_narrative.py` using Gemini or offline mode.
8. Verify the numeric accuracy checks and inspect `narrator/sample_output.txt`.

The following is the repository structure of the capstone project.

<repo>/
├── README.md
├── sql/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── reports.sql
├── data/
│   ├── customers.csv
│   ├── products.csv
│   └── orders.csv
├── analysis/
│   ├── clean_and_eda.py
│   └── visualize.py
├── visualizations/
│   ├── return_rate_by_payment.png
│   └── monthly_revenue_trend.png
└── narrator/
    ├── findings.json
    └── generate_narrative.py

