import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "loblaw.db"
OUT_DIR = ROOT / "outputs"

def main():
    conn = sqlite3.connect(DB_PATH)
    OUT_DIR.mkdir(exist_ok=True)

    # melanoma + miraclib + PBMC where time_from_treatment_start is 0
    cohort = pd.read_sql("""
        SELECT sa.subject_id, su.project, su.response, su.sex
        FROM samples sa
        JOIN subjects su ON sa.subject_id = su.subject_id
        WHERE su.condition = 'melanoma'
          AND su.treatment = 'miraclib'
          AND sa.sample_type = 'PBMC'
          AND sa.time_from_treatment_start = 0
    """, conn)

    """
    We need to determine:
    1. How many samples from each project
    2. How many subjects were responders/non-responders 
    3. How many subjects were males/females
    """

    #1. samples per project
    cohort.groupby("project").size().reset_index(name="n_samples") \
          .to_csv(OUT_DIR / "baseline_samples_per_project.csv", index=False)
    
    #2. subject counts by response and #3. sex
    breakdown = pd.concat([
        cohort.groupby("response").size().reset_index(name="n_subjects").rename(columns={"response": "value"}).assign(category="response"),
        cohort.groupby("sex").size().reset_index(name="n_subjects").rename(columns={"sex": "value"}).assign(category="sex"),
    ])[["category", "value", "n_subjects"]]
    breakdown.to_csv(OUT_DIR / "baseline_subject_breakdown.csv", index=False)


    # Considering Melanoma males, what is the average number of B cells for responders at time=0? Use two decimals.
    # b-cell count for melanoma male responders at time = 0
    avg_bcell = pd.read_sql("""
        SELECT AVG(sa.b_cell) AS mean_b_cell
        FROM samples sa
        JOIN subjects su ON sa.subject_id = su.subject_id
        WHERE su.condition = 'melanoma'
          AND su.sex = 'M'
          AND su.response = 'yes'
          AND sa.time_from_treatment_start = 0
        """, conn).iloc[0, 0]
    (OUT_DIR / "baseline_b_cell_responders.txt").write_text(f"{avg_bcell:.2f}\n")

    # close sql connection
    conn.close()

    print(f"Considering Melanoma males, what is the average number of B cells for responders at time=0? Answer: {avg_bcell:.2f}")

if __name__ == "__main__":
    main()
