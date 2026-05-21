from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"

st.set_page_config(page_title="Loblaw Bio Cell-Count Analysis", layout="wide")


# load all the artifacts
@st.cache_data
def load_artifacts():
    return {
        "frequencies":     pd.read_csv(OUT / "cell_frequencies.csv"),
        "responder_stats": pd.read_csv(OUT / "responder_stats.csv"),
        "samples_per_proj": pd.read_csv(OUT / "baseline_samples_per_project.csv"),
        "breakdown":       pd.read_csv(OUT / "baseline_subject_breakdown.csv"),
        "bcell_avg":       (OUT / "baseline_b_cell_responders.txt").read_text().strip(),
        "boxplot_path":    OUT / "boxplot_responders_vs_nonresponders.png",
    }


data = load_artifacts()


# header
st.title("Loblaw Bio Cell-Count Analysis")
st.markdown(
    "Immune cell-population analysis for the miraclib clinical trial. "
    "Data from `cell-count.csv`, analyzed across three projects."
)

# frequency table statistics
freq = data["frequencies"]
n_samples = freq["sample"].nunique()
col1, col2, col3 = st.columns(3)
col1.metric("Samples",      f"{n_samples:,}")
col2.metric("Populations",  freq["population"].nunique())
col3.metric("Total rows",   f"{len(freq):,}")

st.divider()


# cell frequencies
st.header("Cell-Population Frequencies")
st.caption("Relative frequency of each immune cell population per sample.")

# filter functionality for the cell frequencies
st.sidebar.header("Filters: Cell Frequencies")
pop_filter = st.sidebar.multiselect(
    "Population",
    options=sorted(freq["population"].unique()),
    default=sorted(freq["population"].unique()),
)
sample_filter = st.sidebar.text_input(
    "Sample ID contains",
    value="",
    help="e.g. 'sample001' to filter to samples starting with sample001",
)

filtered = freq[freq["population"].isin(pop_filter)]
if sample_filter:
    filtered = filtered[filtered["sample"].str.contains(sample_filter, case=False)]

st.dataframe(filtered, use_container_width=True, height=350)
st.caption(f"Showing {len(filtered):,} of {len(freq):,} rows.")

st.divider()


# b-cell responders vs non-responders
st.header("Responders vs Non-Responders")
st.markdown(
    "Comparison of cell-population frequencies between responders and "
    "non-responders to miraclib in melanoma patients (PBMC samples only). "
    "Statistical test: Mann-Whitney U with Bonferroni correction."
)

col_plot, col_stats = st.columns([3, 2])

with col_plot:
    if data["boxplot_path"].exists():
        st.image(str(data["boxplot_path"]), use_container_width=True)
    else:
        st.warning("Boxplot not found — run `make pipeline` to generate it.")

with col_stats:
    stats = data["responder_stats"].copy()
    stats["p_value"]            = stats["p_value"].map(lambda x: f"{x:.2e}")
    stats["p_value_bonferroni"] = stats["p_value_bonferroni"].map(lambda x: f"{x:.2e}")
    stats["median_responders"]     = stats["median_responders"].round(2)
    stats["median_non_responders"] = stats["median_non_responders"].round(2)
    st.dataframe(
        stats[[
            "population", "median_responders", "median_non_responders",
            "p_value", "p_value_bonferroni", "significant_bonferroni"
        ]],
        use_container_width=True,
        hide_index=True,
    )

# significant populations
sig = data["responder_stats"][data["responder_stats"]["significant_bonferroni"]]
if len(sig):
    pops = ", ".join(f"`{p}`" for p in sig["population"])
    st.success(f"Significant populations (Bonferroni p<0.05): {pops}")
else:
    st.info("No populations reached Bonferroni-corrected significance.")

st.divider()


# part 4: the baseline (time=0)
st.header("Baseline Cohort (Time From Treatment Start is 0)")
st.markdown(
    "Melanoma patients on miraclib, PBMC samples at baseline "
    "(`time_from_treatment_start = 0`)."
)

col_proj, col_resp, col_sex = st.columns(3)

with col_proj:
    st.subheader("Samples per project")
    st.dataframe(data["samples_per_proj"], hide_index=True, use_container_width=True)

breakdown = data["breakdown"]
with col_resp:
    st.subheader("By b-cell response")
    st.dataframe(
        breakdown[breakdown["category"] == "response"][["value", "n_subjects"]],
        hide_index=True, use_container_width=True,
    )

with col_sex:
    st.subheader("By sex")
    st.dataframe(
        breakdown[breakdown["category"] == "sex"][["value", "n_subjects"]],
        hide_index=True, use_container_width=True,
    )

st.subheader("Average B-cell count, melanoma male responders at baseline")
st.metric("mean b_cell", data["bcell_avg"])

st.divider()
st.caption(
    "Dashboard reads pre-computed artifacts from `outputs/`. "
    "To regenerate them, run `make pipeline`."
)
