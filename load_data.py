import sqlite3
from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "data" / "cell-count.csv"
DB_PATH = ROOT / "loblaw.db"
SCHEMA_PATH = ROOT / "schema.sql"


def main():
    #read the CSV
    print(f"Reading {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    print(f"  {len(df)} rows loaded")

    #connect to sqlite
    conn = sqlite3.connect(DB_PATH)

    #drop existing tables and recreate from schema.sql
    conn.execute("DROP TABLE IF EXISTS samples;")
    conn.execute("DROP TABLE IF EXISTS subjects;")
    schema_sql = SCHEMA_PATH.read_text()
    conn.executescript(schema_sql)

    #build the subjects table: one row per subject.
    subjects = (
        df[["subject", "project", "condition", "age", "sex", "treatment", "response"]]
        .drop_duplicates(subset="subject")
        .rename(columns={"subject": "subject_id"})
    )
    subjects.to_sql("subjects", conn, if_exists="append", index=False)
    print(f"  Inserted {len(subjects)} subjects")

    #build the samples table (one row per sample)
    samples = df[[
        "sample", "subject", "sample_type", "time_from_treatment_start",
        "b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte",
    ]].rename(columns={"sample": "sample_id", "subject": "subject_id"})
    samples.to_sql("samples", conn, if_exists="append", index=False)
    print(f"  Inserted {len(samples)} samples")

    conn.commit()
    conn.close()
    print(f"Done. Database at {DB_PATH}")


if __name__ == "__main__":
    main()