import sqlite3
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "loblaw.db"
FREQ_PATH = ROOT / "outputs" / "cell_frequencies.csv"
STATS_OUT = ROOT / "outputs" / "responder_stats.csv"
PLOT_OUT = ROOT / "outputs" / "boxplot_responders_vs_nonresponders.png"

POPULATIONS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]


def main():
    # melanoma + miraclib + PBMC
    conn = sqlite3.connect(DB_PATH)
    cohort_samples = pd.read_sql("""
        SELECT sa.sample_id, su.response
        FROM samples sa
        JOIN subjects su ON sa.subject_id = su.subject_id
        WHERE su.condition = 'melanoma'
          AND su.treatment = 'miraclib'
          AND sa.sample_type = 'PBMC'
          AND su.response IS NOT NULL
    """, conn)
    conn.close()
    print(f"Cohort: {len(cohort_samples)} samples")
    print(f"  Responders:     {(cohort_samples['response']=='yes').sum()}")
    print(f"  Non-responders: {(cohort_samples['response']=='no').sum()}")

    # load the Part 2 frequencies and filter to this cohort
    freq = pd.read_csv(FREQ_PATH)
    freq = freq.merge(cohort_samples, left_on="sample", right_on="sample_id")
    print(f"\nFrequency rows in cohort: {len(freq)} (expect cohort_samples × 5)")

    # run Mann-Whitney for each population
    results = []
    for pop in POPULATIONS:
        pop_df = freq[freq["population"] == pop]
        responders     = pop_df.loc[pop_df["response"] == "yes", "percentage"]
        non_responders = pop_df.loc[pop_df["response"] == "no",  "percentage"]

        stat, p = mannwhitneyu(responders, non_responders, alternative="two-sided")

        results.append({
            "population":             pop,
            "n_responders":           len(responders),
            "n_non_responders":       len(non_responders),
            "median_responders":      responders.median(),
            "median_non_responders":  non_responders.median(),
            "u_statistic":            stat,
            "p_value":                p,
        })

    stats_df = pd.DataFrame(results)

    # bonferroni correction (multiply each p-value by the number of tests)
    stats_df["p_value_bonferroni"] = (stats_df["p_value"] * len(POPULATIONS)).clip(upper=1.0)
    stats_df["significant_bonferroni"] = stats_df["p_value_bonferroni"] < 0.05

    # save the stats table.
    STATS_OUT.parent.mkdir(exist_ok=True)
    stats_df.to_csv(STATS_OUT, index=False)
    print(f"\nWrote {STATS_OUT}")
    print(stats_df.to_string(index=False))

    # make boxplot: 5 panels, one per population, responder vs non-responder
    sns.set_style("whitegrid")
    g = sns.catplot(
        data=freq,
        x="response",
        y="percentage",
        col="population",
        col_order=POPULATIONS,
        order=["yes", "no"],
        kind="box",
        height=4,
        aspect=0.7,
        sharey=False,
    )
    g.set_axis_labels("Response", "Relative frequency (%)")
    g.set_titles("{col_name}")
    g.fig.suptitle(
        "Melanoma + miraclib + PBMC: responders vs non-responders",
        y=1.05,
    )

    # annotation
    sig_pops = set(stats_df.loc[stats_df["significant_bonferroni"], "population"])
    for ax, pop in zip(g.axes.flat, POPULATIONS):
        if pop in sig_pops:
            ax.set_title(f"{pop} *", fontweight="bold")

    g.savefig(PLOT_OUT, dpi=150, bbox_inches="tight")
    plt.close(g.fig)
    print(f"\nWrote {PLOT_OUT}")

    # print summary to console
    sig = stats_df[stats_df["significant_bonferroni"]]
    if len(sig):
        print(f"\nSignificant populations (Bonferroni p<0.05):")
        for _, row in sig.iterrows():
            direction = "higher" if row["median_responders"] > row["median_non_responders"] else "lower"
            print(f"  {row['population']}: responders {direction} "
                  f"(median {row['median_responders']:.2f}% vs {row['median_non_responders']:.2f}%, "
                  f"p={row['p_value']:.2e}, Bonferroni p={row['p_value_bonferroni']:.2e})")
    else:
        print("\nNo populations reached Bonferroni-corrected significance.")


if __name__ == "__main__":
    main()
