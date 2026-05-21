
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "loblaw.db"
OUTPUT_PATH = ROOT / "outputs" / "cell_frequencies.csv"

POPULATIONS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]


def main():
    # fetch samples table
    conn = sqlite3.connect(DB_PATH)
    samples = pd.read_sql("SELECT * FROM samples", conn)
    conn.close()
    print(f"Loaded {len(samples)} samples")

    # compute total count per sample (calculate a sum accross the 5 population columns)
    samples["total_count"] = samples[POPULATIONS].sum(axis=1)

    #melt from wide to long
    long_df = samples.melt(
        id_vars=["sample_id", "total_count"],
        value_vars=POPULATIONS,
        var_name="population",
        value_name="count",
    )

    # calculate the percentage
    long_df["percentage"] = (long_df["count"] / long_df["total_count"]) * 100

    # add percentage column to the long dataframe
    result = long_df.rename(columns={"sample_id": "sample"})[
        ["sample", "total_count", "population", "count", "percentage"]
    ]

    # write the output
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    result.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(result)} rows to {OUTPUT_PATH}")

    # preview
    print("\nPreview (first sample's 5 rows):")
    print(result.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
