# Loblaw Bio Project

## Instructions to Run
This project is designed to run in GitHub Codespaces, but works locally on Mac or Linux as well. From the repository root:

```bash
make setup       # install Python dependencies from requirements.txt
make pipeline    # run the full analysis end-to-end
make dashboard   # launch the dashboard at http://localhost:8501
```

`make pipeline` runs the four scripts in order: `load_data.py` creates the database, then `frequencies.py`, `responders.py`, and `baseline.py` produce the analysis outputs in the `outputs/` folder.

If `make` isn't available, the scripts can be run directly:

```bash
pip install -r requirements.txt
python load_data.py
python analysis/frequencies.py
python analysis/responders.py
python analysis/baseline.py
python -m streamlit run dashboard/app.py
```

To start fresh, `make clean` removes the database and outputs folder.

## Dashboard
Link: [https://loblaw-bio-nick.streamlit.app/](https://loblaw-bio-nick.streamlit.app/)

## Overview

**Part 1: Data Management**\
In order to structure/organize the data into a relational database schema, I decided to split the CSV into two related tables.
The first table, subjects, holds the patient information: demographics, condition, treatment, response.
The second table, samples, holds the data for each blood sample: timepoint, sample type, cell counts.
In the second table, I added a link (subject_id) that references the first table to which subject the sample came from.

**Part 2: Initial Analysis - Data Overview**\
“What is the frequency of each cell type in each sample?”
In order to answer this question, I wrote a new python program: frequencies.py
The goal of this program is to produce the relative frequency of each immune cell population as a percentage of the total cell count for that sample.
The outputs from frequency.py are stored in the CSV file cell_frequencies.csv

**Part 3: Statistical Analysis**\
To identify patterns that might predict treatment response, I wrote responders.py, which filters the data to melanoma patients on miraclib (PBMC samples only) 
and compares the relative frequencies of each cell population between responders and non-responders using a Mann-Whitney U test, with a Bonferroni correction for the five comparisons. 
The outputs are responder_stats.csv (test statistics and p-values per population) and boxplot_responders_vs_nonresponders.png (a faceted boxplot of the comparisons).

**Part 4: Data Subset Analysis**\
To explore early treatment effects, I wrote baseline.py, which filters the data to melanoma patients on miraclib (PBMC samples only) at baseline (time_from_treatment_start = 0)
and breaks the cohort down by project, response, and sex. The program also computes the average B-cell count for melanoma male responders at baseline.
The outputs are baseline_samples_per_project.csv, baseline_subject_breakdown.csv, and baseline_b_cell_responders.txt.

**Notes on the Data**\
While building the cohort filters, I noticed that project 2 (prj2) only collected whole-blood (WB) samples — no PBMC samples at all.
This means prj2 doesn't appear in the PBMC-filtered outputs of Parts 3 and 4, even though it contains 478 melanoma subjects.

## Schema Explanation

The data is loaded into a SQLite database with two related tables, defined in `schema.sql`:

**subjects** — one row per subject (3,500 rows)
| Column | Type | Notes |
|---|---|---|
| subject_id | TEXT | Primary key |
| project | TEXT | prj1 / prj2 / prj3 |
| condition | TEXT | melanoma / carcinoma / healthy |
| age | INTEGER | |
| sex | TEXT | M / F |
| treatment | TEXT | miraclib / phauximab / none |
| response | TEXT | yes / no / NULL (untreated subjects) |

**samples** — one row per biological sample (10,500 rows)
| Column | Type | Notes |
|---|---|---|
| sample_id | TEXT | Primary key |
| subject_id | TEXT | Foreign key → subjects |
| sample_type | TEXT | PBMC / WB |
| time_from_treatment_start | INTEGER | 0 / 7 / 14 days |
| b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte | INTEGER | Raw cell counts |

**Rationale.** The CSV is flat — each subject's demographics are repeated across their three timepoint rows. Splitting subject-level attributes into their own table removes that duplication, and the foreign key on `subject_id` rejoins them when a query needs both. The cell counts stay as columns on `samples` (wide format) rather than a separate long-format table, because for a fixed panel of five populations the wide layout is simpler to query.

**Scaling**
- Subject attributes are stored once per subject, not per sample. Adding new timepoints adds one row to `samples` instead of a full re-copy of demographics — meaningful at scale, and a guarantee that no two rows can disagree on a subject's age or sex.
- `project` is a column, not a separate table per project. Queries like "samples per project" or "responders by project" are `GROUP BY project` and don't change as the number of projects grows. Adding a new project is one row of data, not a schema migration.
- Common analytical filters (`condition`, `treatment`, `sample_type`, `time_from_treatment_start`) live on indexable columns, so cohort queries stay fast as the data grows.
- The main tradeoff: if a sixth cell population is ever added, the wide layout requires an `ALTER TABLE` instead of just an insert. For a fixed panel of five populations this is fine; if populations are expected to grow, a long-format `cell_counts` table would be the better call.




