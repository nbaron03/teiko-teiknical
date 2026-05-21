Part 1: Data Management
In order to structure/organize the data into a relational database schema, I decided to split the CSV into two related tables.
The first table, subjects, holds the patient information: demographics, condition, treatment, response.
The second table, samples, holds the data for each blood sample: timepoint, sample type, cell counts.
In the second table, I added a link (subject_id) that references the first table to which subject the sample came from.

Part 2: Initial Analysis - Data Overview
“What is the frequency of each cell type in each sample?”
In order to answer this question, I wrote a new python program: frequencies.py
The goal of this program is to produce the relative frequency of each immune cell population as a percentage of the total cell count for that sample.
The outputs from frequency.py are stored in the CSV file cell_frequencies.csv

Part 3: Statistical Analysis
To identify patterns that might predict treatment response, I wrote responders.py, which filters the data to melanoma patients on miraclib (PBMC samples only) 
and compares the relative frequencies of each cell population between responders and non-responders using a Mann-Whitney U test, with a Bonferroni correction for the five comparisons. 
The outputs are responder_stats.csv (test statistics and p-values per population) and boxplot_responders_vs_nonresponders.png (a faceted boxplot of the comparisons).

Part 4: Data Subset Analysis
