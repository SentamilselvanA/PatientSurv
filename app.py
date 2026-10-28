"""Patient Survival Analytics — Premium Redesign."""

import io, logging, os, sys, datetime
import numpy as np
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from config.settings import APP_TITLE, DEFAULT_ALPHA, RANDOM_SEED, REPORT_DIR, DEFAULT_TIME_UNIT
from src.data_loader import generate_synthetic_dataset, load_file, get_excel_sheet_names, check_file_size, SYNTHETIC_SCHEMA
from src.data_validation import validate_dataset
from src.preprocessing import preprocess, add_age_groups
from src.descriptive_statistics import numeric_summary, categorical_summary, outcome_summary, group_outcome_summary
from src.exploratory_analysis import dataset_overview, bivariate_summary
from src.hypothesis_testing import (
    two_proportion_test, chi_square_test, two_group_numeric_test,
    kruskal_wallis_test, apply_multiple_testing_correction
)
from src.survival_analysis import fit_kaplan_meier, km_summary, km_by_group, log_rank_test, fit_cox, cox_summary_table
from src.visualization import (
    plot_histogram, plot_boxplot, plot_bar, plot_missing_heatmap,
    plot_outcome_pie, plot_group_proportions, plot_correlation_heatmap,
    plot_kaplan_meier, plot_at_risk_table, plot_cox_forest, plot_follow_up_distribution
)
from src.interpretation import (
    interpret_test_result, interpret_missing_data,
    interpret_km_result, interpret_cox_result, generate_findings_summary
)
from src.reproducibility import build_reproducibility_record, reproducibility_to_text
from src.report_generator import generate_pdf_report, export_csv
from src.ui_theme import (
    THEME_CSS, DARK_MODE_CSS, metric_card_html, kpi_card_html,
    research_card_html, page_header_html, section_title_html,
    nav_brand_html, build_nav_html, _DNA_SVG, card_header_html, footer_html
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Survival Analytics",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PAGES = ["Home", "Patient Analytics", "EDA", "Hypothesis Testing", "Survival Analysis", "Reports"]
PAGE_ICONS = {
    "Home": "🏠",
    "Patient Analytics": "📊",
    "EDA": "🔍",
    "Hypothesis Testing": "🔬",
    "Survival Analysis": "📈",
    "Reports": "📄",
}

# ── Session state init ──────────────────────────────────────────────────────
def _init():
    defaults = {
        "page": "Home",
        "dark_mode": False,
        "df_raw": None,
        "df_clean": None,
        "prep_log": None,
        "val_report": None,
        "dataset_name": "Synthetic Dataset (n=1000)",
        "dataset_source": "Generated using fixed random seed (synthetic)",
        "col_map": {
            "id": "patient_id", "age": "age", "sex": "sex",
            "stage": "stage", "time": "follow_up_months",
            "event": "event", "outcome": "survival_5yr",
        },
        "alpha": DEFAULT_ALPHA,
        "time_unit": DEFAULT_TIME_UNIT,
        "test_results": [],
        "km_fitters": {},
        "cox_result": None,
        "outcome_sum": {},
        "findings_text": "",
        "dataset_loaded": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ── Auto-load synthetic dataset once ───────────────────────────────────────
def _auto_load():
    if st.session_state.dataset_loaded:
        return
    df = generate_synthetic_dataset(n=1000, seed=RANDOM_SEED)
    cm = st.session_state.col_map
    val = validate_dataset(df, id_col=cm.get("id"), time_col=cm.get("time"),
                           event_col=cm.get("event"), age_col=cm.get("age"))
    df_c, prep_log = preprocess(df, id_col=cm.get("id"), time_col=cm.get("time"),
                                event_col=cm.get("event"), age_col=cm.get("age"),
                                outcome_col=cm.get("outcome"))
    df_c = add_age_groups(df_c, cm["age"])
    st.session_state.df_raw = df
    st.session_state.df_clean = df_c
    st.session_state.prep_log = prep_log
    st.session_state.val_report = val
    st.session_state.dataset_loaded = True

_auto_load()

# ── Theme ───────────────────────────────────────────────────────────────────
dark = st.session_state.dark_mode

# Inject base CSS
st.markdown(THEME_CSS, unsafe_allow_html=True)
# Inject dark mode overrides
if dark:
    st.markdown(DARK_MODE_CSS, unsafe_allow_html=True)

# Apply plotly template based on theme
PLOTLY_TEMPLATE = "plotly_dark" if dark else "plotly_white"
PLOTLY_BG = "#111726" if dark else "#FFFFFF"
PLOTLY_PAPER = "#111726" if dark else "#FFFFFF"
PLOTLY_FONT = "#F8FAFC" if dark else "#0F172A"

def _theme_fig(fig):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=PLOTLY_PAPER,
        plot_bgcolor=PLOTLY_BG,
        font_color=PLOTLY_FONT,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig

# ── Navigation callbacks & helper ──────────────────────────────────────────
def _on_nav_change():
    if "nav_selection" in st.session_state and st.session_state.nav_selection:
        st.session_state.page = st.session_state.nav_selection

def _navigate_to(target_page: str):
    st.session_state.page = target_page
    st.session_state.nav_selection = target_page
    st.rerun()

# ── Unified Sticky Navigation Bar ───────────────────────────────────────────
with st.container(key="sa-navbar"):
    col_brand, col_nav, col_toggle = st.columns([2.5, 7.1, 0.6], vertical_alignment="center")
    with col_brand:
        st.markdown(nav_brand_html(), unsafe_allow_html=True)
    with col_nav:
        if "nav_selection" not in st.session_state:
            st.session_state.nav_selection = st.session_state.page
        st.pills(
            "Navigation",
            PAGES,
            selection_mode="single",
            required=True,
            default=st.session_state.page,
            format_func=lambda x: f"{PAGE_ICONS.get(x, '')} {x}",
            label_visibility="collapsed",
            key="nav_selection",
            on_change=_on_nav_change,
        )
    with col_toggle:
        if st.button("🌙" if not dark else "☀️", key="theme_toggle", help="Toggle light / dark mode"):
            st.session_state.dark_mode = not dark
            st.rerun()

page = st.session_state.page
df = st.session_state.df_clean
cm = st.session_state.col_map

# ── Page Content Wrapper ────────────────────────────────────────────────────
with st.container(key="sa-page-body"):

    # ════════════════════════════════════════════
    # PAGE: HOME
    # ════════════════════════════════════════════
    if page == "Home":
        # ── Hero ──
        out_col = cm.get("outcome", "survival_5yr")
        age_col = cm.get("age", "age")
        time_col = cm.get("time", "follow_up_months")
        event_col = cm.get("event", "event")

        n_total = len(df) if df is not None else 0
        event_rate = "—"
        median_age = "—"
        median_fu = "—"

        if df is not None:
            if event_col in df.columns:
                ev = df[event_col].dropna()
                event_rate = f"{ev.mean()*100:.1f}%"
            if age_col in df.columns:
                median_age = f"{df[age_col].median():.0f} yrs"
            if time_col in df.columns:
                median_fu = f"{df[time_col].median():.1f} mo"

        hero_left = f"""
<div class="hero-section">
  <div>
    <div class="hero-eyebrow">🧬 Clinical Biostatistics · Research Edition</div>
    <h1 class="hero-title">Understanding<br><span class="grad-text">Patient Survival</span><br>Outcomes</h1>
    <p class="hero-desc">
      Explore patient survival outcomes through rigorous statistical analysis, demographic comparisons,
      and time-to-event research. Discover meaningful patterns, quantify uncertainty,
      and evaluate clinical evidence behind patient cohorts.
    </p>
  </div>
  <div class="metric-grid">
    {metric_card_html("👥", "Total Patients", f"{n_total:,}", "Analytical sample", synthetic=True)}
    {metric_card_html("📉", "Observed Event Rate", event_rate, "Proportion with event (not survival probability)")}
    {metric_card_html("🎂", "Median Age", median_age, "At diagnosis")}
    {metric_card_html("📅", "Median Follow-up", median_fu, "Months from diagnosis")}
  </div>
</div>
"""
        st.markdown(hero_left, unsafe_allow_html=True)

        # CTA buttons
        c1, c2, c3 = st.columns([2, 2, 6])
        with c1:
            if st.button("Explore Analytics →", type="primary", use_container_width=True):
                _navigate_to("Patient Analytics")
        with c2:
            if st.button("View Methodology", use_container_width=True):
                _navigate_to("Reports")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Research cards with integrated navigation ──
        st.markdown(section_title_html(
            "Explore Analytical Modules",
            "Four specialized stages from exploratory data analysis to exportable research reports."
        ), unsafe_allow_html=True)

        rc1, rc2, rc3, rc4 = st.columns(4)
        with rc1:
            with st.container(border=True):
                st.markdown(research_card_html(
                    "🔍", "Data Exploration",
                    "Understand patient distributions, demographic characteristics, and data quality metrics."
                ), unsafe_allow_html=True)
                if st.button("Open EDA →", key="rc1", use_container_width=True):
                    _navigate_to("EDA")
        with rc2:
            with st.container(border=True):
                st.markdown(research_card_html(
                    "🔬", "Statistical Testing",
                    "Perform two-proportion tests, Welch's t-tests, and multiple testing corrections."
                ), unsafe_allow_html=True)
                if st.button("Open Testing →", key="rc2", use_container_width=True):
                    _navigate_to("Hypothesis Testing")
        with rc3:
            with st.container(border=True):
                st.markdown(research_card_html(
                    "📈", "Survival Analysis",
                    "Fit Kaplan–Meier curves, compute log-rank statistics, and analyze Cox PH models."
                ), unsafe_allow_html=True)
                if st.button("Open Survival →", key="rc3", use_container_width=True):
                    _navigate_to("Survival Analysis")
        with rc4:
            with st.container(border=True):
                st.markdown(research_card_html(
                    "📄", "Research Findings",
                    "Review synthesized clinical findings, export datasets, and generate PDF reports."
                ), unsafe_allow_html=True)
                if st.button("Open Reports →", key="rc4", use_container_width=True):
                    _navigate_to("Reports")

    # ════════════════════════════════════════════
    # PAGE: PATIENT ANALYTICS
    # ════════════════════════════════════════════
    elif page == "Patient Analytics":
        st.markdown(page_header_html(
            "Patient Analytics",
            "Explore patient demographics, clinical outcomes, event rates, and follow-up patterns.",
            dataset_label=f"{st.session_state.dataset_name} &middot; {len(df):,} records"
        ), unsafe_allow_html=True)

        out_col   = cm.get("outcome", "survival_5yr")
        age_col   = cm.get("age", "age")
        time_col  = cm.get("time", "follow_up_months")
        event_col = cm.get("event", "event")

        # ── Inline filters ──
        with st.expander("🎛 Cohort Filters", expanded=False):
            dff = df.copy()
            f_cols = st.columns(3)
            col_idx = 0
            if age_col in df.columns:
                age_min, age_max = int(df[age_col].min()), int(df[age_col].max())
                with f_cols[col_idx % 3]:
                    age_range = st.slider("Age range", age_min, age_max, (age_min, age_max), key="filt_age")
                dff = dff[dff[age_col].between(*age_range)]
                col_idx += 1
            for filt_col in ["sex", "stage", "subtype", "treatment", "region"]:
                if filt_col in df.columns:
                    opts = ["All"] + sorted(df[filt_col].dropna().unique().tolist())
                    with f_cols[col_idx % 3]:
                        sel_f = st.selectbox(filt_col.capitalize(), opts, key=f"filt_{filt_col}")
                    if sel_f != "All":
                        dff = dff[dff[filt_col] == sel_f]
                    col_idx += 1
            st.caption(f"Filtered Cohort: {len(dff):,} of {len(df):,} patients")

        # ── KPI strip ──
        n_ev = int((dff[event_col] == 1).sum()) if event_col in dff.columns else 0
        n_nev = len(dff) - n_ev
        ev_pct = f"{n_ev/len(dff)*100:.1f}%" if len(dff) else "—"
        med_age = f"{dff[age_col].median():.0f}" if age_col in dff.columns else "—"
        med_fu  = f"{dff[time_col].median():.1f}" if time_col in dff.columns else "—"

        kpi_html = f"""
<div class="kpi-strip">
  {kpi_card_html(f"{len(dff):,}", "Cohort Size", "👥")}
  {kpi_card_html(str(n_ev), "Events Observed", "📉")}
  {kpi_card_html(str(n_nev), "Censored / Safe", "✅")}
  {kpi_card_html(ev_pct, "Event Rate", "📊")}
  {kpi_card_html(med_age, "Median Age", "🎂")}
  {kpi_card_html(med_fu + " mo", "Median Follow-up", "📅")}
</div>
"""
        st.markdown(kpi_html, unsafe_allow_html=True)

        # ── Charts grid with border containers ──
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            with st.container(border=True):
                st.markdown(card_header_html("Outcome Distribution", "📊"), unsafe_allow_html=True)
                if event_col in dff.columns:
                    fig = plot_outcome_pie(n_ev, n_nev, "Event (1)", "No Event (0)")
                    st.plotly_chart(_theme_fig(fig), use_container_width=True)

        with r1c2:
            with st.container(border=True):
                st.markdown(card_header_html("Age Distribution", "🎂"), unsafe_allow_html=True)
                if age_col in dff.columns:
                    fig = plot_histogram(dff, age_col, f"Age Distribution (n={len(dff):,})")
                    st.plotly_chart(_theme_fig(fig), use_container_width=True)

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            with st.container(border=True):
                st.markdown(card_header_html("Cohort by Biological Sex", "👥"), unsafe_allow_html=True)
                if "sex" in dff.columns:
                    fig = plot_bar(dff, "sex", "Distribution by Sex")
                    st.plotly_chart(_theme_fig(fig), use_container_width=True)

        with r2c2:
            with st.container(border=True):
                st.markdown(card_header_html("Cohort by Disease Stage", "🏷️"), unsafe_allow_html=True)
                if "stage" in dff.columns:
                    fig = plot_bar(dff, "stage", "Distribution by Stage")
                    st.plotly_chart(_theme_fig(fig), use_container_width=True)

        r3c1, r3c2 = st.columns(2)
        with r3c1:
            with st.container(border=True):
                st.markdown(card_header_html("Event Rate by Disease Stage", "📉"), unsafe_allow_html=True)
                if "stage" in dff.columns and out_col in dff.columns:
                    grp_sum = group_outcome_summary(dff, out_col, "stage")
                    fig = plot_group_proportions(grp_sum, "group")
                    st.plotly_chart(_theme_fig(fig), use_container_width=True)

        with r3c2:
            with st.container(border=True):
                st.markdown(card_header_html("Event Rate by Treatment Arm", "💊"), unsafe_allow_html=True)
                if "treatment" in dff.columns and out_col in dff.columns:
                    grp_sum2 = group_outcome_summary(dff, out_col, "treatment")
                    fig = plot_group_proportions(grp_sum2, "group")
                    st.plotly_chart(_theme_fig(fig), use_container_width=True)

        # Upload replacement dataset
        with st.expander("⬆️ Replace dataset (Advanced Upload)"):
            st.caption("Upload a CSV or Excel file to replace the synthetic dataset.")
            uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"], key="adv_upload")
            if uploaded:
                try:
                    raw_bytes = uploaded.read()
                    check_file_size(raw_bytes)
                    buf = io.BytesIO(raw_bytes)
                    sheet = 0
                    if uploaded.name.endswith((".xlsx", ".xls")):
                        sheets = get_excel_sheet_names(io.BytesIO(raw_bytes))
                        sheet = st.selectbox("Worksheet", sheets, key="adv_sheet")
                    new_df = load_file(io.BytesIO(raw_bytes), uploaded.name, sheet_name=sheet)
                    st.session_state.df_raw = new_df
                    st.session_state.dataset_name = uploaded.name
                    st.session_state.dataset_source = f"User upload: {uploaded.name}"
                    st.session_state.dataset_loaded = False
                    st.success(f"Loaded {len(new_df):,} rows. Re-map columns below and click Apply.")
                    cols = [""] + new_df.columns.tolist()
                    new_cm = {}
                    cc1, cc2, cc3 = st.columns(3)
                    with cc1:
                        new_cm["id"]      = st.selectbox("Patient ID", cols, key="nm_id")
                        new_cm["age"]     = st.selectbox("Age", cols, key="nm_age")
                    with cc2:
                        new_cm["time"]    = st.selectbox("Follow-up Time", cols, key="nm_time")
                        new_cm["event"]   = st.selectbox("Event Indicator", cols, key="nm_event")
                    with cc3:
                        new_cm["outcome"] = st.selectbox("Binary Outcome", cols, key="nm_out")
                        new_cm["stage"]   = st.selectbox("Stage", cols, key="nm_stage")
                    if st.button("Apply New Dataset", key="apply_new", type="primary"):
                        st.session_state.col_map = {k: v for k, v in new_cm.items() if v}
                        val = validate_dataset(new_df, id_col=new_cm.get("id") or None,
                                              time_col=new_cm.get("time") or None,
                                              event_col=new_cm.get("event") or None)
                        df_c, prep_log = preprocess(new_df, id_col=new_cm.get("id") or None,
                                                    time_col=new_cm.get("time") or None,
                                                    event_col=new_cm.get("event") or None,
                                                    outcome_col=new_cm.get("outcome") or None)
                        if new_cm.get("age") and new_cm["age"] in df_c.columns:
                            df_c = add_age_groups(df_c, new_cm["age"])
                        st.session_state.df_clean = df_c
                        st.session_state.prep_log = prep_log
                        st.session_state.val_report = val
                        st.session_state.dataset_loaded = True
                        st.success("Dataset replaced."); st.rerun()
                except Exception as e:
                    st.error(f"Upload error: {e}")

    # ════════════════════════════════════════════
    # PAGE: EDA
    # ════════════════════════════════════════════
    elif page == "EDA":
        st.markdown(page_header_html(
            "Exploratory Data Analysis",
            "Distributions, correlations, missing values, and group comparisons.",
            dataset_label=f"{st.session_state.dataset_name} &middot; {len(df):,} records"
        ), unsafe_allow_html=True)

        out_col   = cm.get("outcome", "survival_5yr")
        age_col   = cm.get("age", "age")
        time_col  = cm.get("time", "follow_up_months")
        event_col = cm.get("event", "event")

        ov = dataset_overview(df, event_col, time_col)

        # Overview metrics
        ov_html = f"""
<div class="kpi-strip">
  {kpi_card_html(f"{ov['n_rows']:,}", "Patients", "👥")}
  {kpi_card_html(str(ov['n_cols']), "Variables", "📋")}
  {kpi_card_html(str(ov['total_missing']), "Missing Values", "⚠️")}
  {kpi_card_html(str(ov['duplicate_rows']), "Duplicates", "🔁")}
  {kpi_card_html(str(len(ov['numeric_cols'])), "Numeric Vars", "🔢")}
  {kpi_card_html(str(len(ov['categorical_cols'])), "Categorical Vars", "🏷️")}
</div>
"""
        st.markdown(ov_html, unsafe_allow_html=True)

        tab_desc, tab_num, tab_cat, tab_miss, tab_corr, tab_group = st.tabs([
            "Descriptive Stats", "Numeric Distributions", "Categorical",
            "Missing Values", "Correlation", "Group Comparisons"
        ])

        with tab_desc:
            with st.container(border=True):
                st.markdown(card_header_html("Numeric Variables Summary", "🔢"), unsafe_allow_html=True)
                num_cols = df.select_dtypes(include="number").columns.tolist()
                st.dataframe(numeric_summary(df, num_cols), use_container_width=True)

            with st.expander("Data Preview (first 20 rows)"):
                st.dataframe(df.head(20), use_container_width=True)

        with tab_num:
            num_cols = df.select_dtypes(include="number").columns.tolist()
            if num_cols:
                sel_num = st.selectbox("Select variable to inspect", num_cols, key="eda_num")
                grp_opt = st.selectbox("Stratify by", ["None"] + df.select_dtypes(include="object").columns.tolist(), key="eda_grp_num")
                c1, c2 = st.columns(2)
                with c1:
                    with st.container(border=True):
                        st.markdown(card_header_html(f"Histogram: {sel_num}", "📊"), unsafe_allow_html=True)
                        st.plotly_chart(_theme_fig(plot_histogram(df, sel_num)), use_container_width=True)
                with c2:
                    with st.container(border=True):
                        st.markdown(card_header_html(f"Box Plot: {sel_num}", "📦"), unsafe_allow_html=True)
                        x_col = None if grp_opt == "None" else grp_opt
                        st.plotly_chart(_theme_fig(plot_boxplot(df, sel_num, x_col)), use_container_width=True)

        with tab_cat:
            cat_cols = df.select_dtypes(include="object").columns.tolist()
            if cat_cols:
                sel_cat = st.selectbox("Select categorical variable", cat_cols, key="eda_cat")
                c1, c2 = st.columns(2)
                with c1:
                    with st.container(border=True):
                        st.markdown(card_header_html(f"Frequency Bar Chart: {sel_cat}", "📊"), unsafe_allow_html=True)
                        st.plotly_chart(_theme_fig(plot_bar(df, sel_cat)), use_container_width=True)
                with c2:
                    with st.container(border=True):
                        st.markdown(card_header_html(f"Frequency Table: {sel_cat}", "📋"), unsafe_allow_html=True)
                        cat_sum = categorical_summary(df, [sel_cat])
                        st.dataframe(cat_sum[sel_cat], use_container_width=True)

        with tab_miss:
            with st.container(border=True):
                st.markdown(card_header_html("Missing Values Heatmap & Diagnostics", "⚠️"), unsafe_allow_html=True)
                st.plotly_chart(_theme_fig(plot_missing_heatmap(df)), use_container_width=True)
                miss_df = pd.DataFrame([
                    {"Column": c,
                     "Missing": int(df[c].isna().sum()),
                     "Missing %": round(df[c].isna().mean()*100, 1),
                     "Note": interpret_missing_data(df[c].isna().mean()*100, c)}
                    for c in df.columns
                ])
                st.dataframe(miss_df, use_container_width=True)

        with tab_corr:
            num_cols = df.select_dtypes(include="number").columns.tolist()
            if len(num_cols) >= 2:
                with st.container(border=True):
                    st.markdown(card_header_html("Correlation Heatmap Matrix", "🔥"), unsafe_allow_html=True)
                    st.plotly_chart(_theme_fig(plot_correlation_heatmap(df, num_cols)), use_container_width=True)
            else:
                st.info("Need at least 2 numeric columns for correlation analysis.")

        with tab_group:
            cat_cols = df.select_dtypes(include="object").columns.tolist()
            if out_col in df.columns and cat_cols:
                grp_col = st.selectbox("Group variable", cat_cols, key="eda_grp_out")
                if grp_col:
                    grp_sum = group_outcome_summary(df, out_col, grp_col)
                    c1, c2 = st.columns(2)
                    with c1:
                        with st.container(border=True):
                            st.markdown(card_header_html("Proportion by Group", "📊"), unsafe_allow_html=True)
                            st.plotly_chart(_theme_fig(plot_group_proportions(grp_sum, "group")), use_container_width=True)
                    with c2:
                        with st.container(border=True):
                            st.markdown(card_header_html("Group Summary Table", "📋"), unsafe_allow_html=True)
                            st.dataframe(grp_sum, use_container_width=True)

        # Validation warnings
        val = st.session_state.val_report
        if val and (val.warnings or val.errors):
            with st.expander("⚠️ Data Quality Warnings"):
                for w in val.warnings:
                    st.warning(w)
                for e in val.errors:
                    st.error(e)

    # ════════════════════════════════════════════
    # PAGE: HYPOTHESIS TESTING
    # ════════════════════════════════════════════
    elif page == "Hypothesis Testing":
        st.markdown(page_header_html(
            "Hypothesis Testing",
            "Statistical comparisons with effect sizes, confidence intervals, and plain-English interpretation.",
            dataset_label=f"{st.session_state.dataset_name} &middot; {len(df):,} records"
        ), unsafe_allow_html=True)

        cat_cols = df.select_dtypes(include="object").columns.tolist()
        num_cols = df.select_dtypes(include="number").columns.tolist()

        # Configuration Card
        with st.container(border=True):
            st.markdown(card_header_html("Test Configuration", "⚙️"), unsafe_allow_html=True)
            cfg1, cfg2, cfg3 = st.columns(3)
            with cfg1:
                test_type = st.selectbox("Test type", [
                    "Two-proportion test (binary, 2 groups)",
                    "Chi-square test (binary, multiple groups)",
                    "Welch's t-test (numeric, 2 groups)",
                    "Kruskal-Wallis test (numeric, multiple groups)",
                ])
            with cfg2:
                alpha = st.slider("Significance level (α)", 0.01, 0.10, st.session_state.alpha, 0.01)
                st.session_state.alpha = alpha
            with cfg3:
                correction = st.selectbox("Multiple-testing correction", ["holm", "fdr_bh", "none"])

        all_results = []

        # Parameters Card
        with st.container(border=True):
            st.markdown(card_header_html("Test Parameters & Execution", "🔬"), unsafe_allow_html=True)

            if "Two-proportion" in test_type:
                p1, p2, p3 = st.columns(3)
                with p1:
                    out_col = st.selectbox("Outcome column", [c for c in df.columns if df[c].nunique() <= 10])
                with p2:
                    grp_col = st.selectbox("Group column", cat_cols)
                if grp_col and out_col:
                    groups = df[grp_col].dropna().unique().tolist()
                    if len(groups) >= 2:
                        with p3:
                            ev_val = st.selectbox("Event value", sorted(df[out_col].dropna().unique().tolist()))
                        g1, g2 = st.columns(2)
                        with g1:
                            g_a = st.selectbox("Group A (reference)", groups, index=0)
                        with g2:
                            g_b = st.selectbox("Group B", groups, index=min(1, len(groups)-1))
                        if st.button("▶ Run Test", type="primary"):
                            with st.spinner("Running statistical test..."):
                                r = two_proportion_test(df, out_col, grp_col, str(g_a), str(g_b), ev_val, alpha)
                                all_results = [r]
                                st.session_state.test_results = all_results

            elif "Chi-square" in test_type:
                p1, p2 = st.columns(2)
                with p1:
                    out_col = st.selectbox("Outcome column", [c for c in df.columns if df[c].nunique() <= 10])
                with p2:
                    grp_col = st.selectbox("Group column", cat_cols)
                if st.button("▶ Run Test", type="primary"):
                    with st.spinner("Running Chi-Square test..."):
                        r = chi_square_test(df, out_col, grp_col, alpha)
                        all_results = [r]
                        st.session_state.test_results = all_results

            elif "Welch" in test_type:
                p1, p2 = st.columns(2)
                with p1:
                    num_col = st.selectbox("Numeric column", num_cols)
                with p2:
                    grp_col = st.selectbox("Group column", cat_cols)
                if grp_col:
                    groups = df[grp_col].dropna().unique().tolist()
                    if len(groups) >= 2:
                        g1, g2 = st.columns(2)
                        with g1:
                            g_a = st.selectbox("Group A", groups, index=0)
                        with g2:
                            g_b = st.selectbox("Group B", groups, index=min(1, len(groups)-1))
                        if st.button("▶ Run Test", type="primary"):
                            with st.spinner("Running Welch's t-test..."):
                                r = two_group_numeric_test(df, num_col, grp_col, str(g_a), str(g_b), alpha)
                                all_results = [r]
                                st.session_state.test_results = all_results

            elif "Kruskal" in test_type:
                p1, p2 = st.columns(2)
                with p1:
                    num_col = st.selectbox("Numeric column", num_cols)
                with p2:
                    grp_col = st.selectbox("Group column", cat_cols)
                if st.button("▶ Run Test", type="primary"):
                    with st.spinner("Running Kruskal-Wallis test..."):
                        r = kruskal_wallis_test(df, num_col, grp_col, alpha)
                        all_results = [r]
                        st.session_state.test_results = all_results

        # Results display
        results_to_show = all_results if all_results else st.session_state.test_results
        if results_to_show:
            if correction != "none" and len(results_to_show) > 1:
                results_to_show = apply_multiple_testing_correction(results_to_show, correction, alpha)

            for i, r in enumerate(results_to_show, 1):
                sig = r.get("significant", False)
                sig_badge = '<span class="sig-yes">✓ Significant</span>' if sig else '<span class="sig-no">✗ Not significant</span>'

                with st.container(border=True):
                    st.markdown(card_header_html(f"Result {i}: {r.get('test_name','')} &nbsp;{sig_badge}", "📋"), unsafe_allow_html=True)
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Sample size (n)", r.get("n", "—"))
                    m2.metric("Test statistic", f"{r.get('statistic', float('nan')):.4f}")
                    m3.metric("p-value", f"{r.get('p_value', float('nan')):.4f}")
                    m4.metric(r.get("effect_label", "Effect size"), f"{r.get('effect_size', float('nan')):.3f}")

                    with st.expander("Full statistical details"):
                        st.markdown(f"**Research question:** {r.get('research_question','')}")
                        st.markdown(f"**H₀:** {r.get('h0','')}")
                        st.markdown(f"**H₁:** {r.get('h1','')}")
                        st.markdown(f"**Test selected:** {r.get('test_name','')} — {r.get('reason','')}")
                        st.markdown(f"**Assumptions:** {r.get('assumptions','')}")
                        if r.get("ci"):
                            st.markdown(f"**95% CI for difference:** ({r['ci'][0]:.4f}, {r['ci'][1]:.4f})")
                        if "p_adjusted" in r:
                            st.markdown(f"**Adjusted p-value ({correction}):** {r['p_adjusted']:.4f}")
                        st.markdown(f"**Limitations:** {r.get('limitations','')}")

                    st.info(interpret_test_result(r))

    # ════════════════════════════════════════════
    # PAGE: SURVIVAL ANALYSIS
    # ════════════════════════════════════════════
    elif page == "Survival Analysis":
        st.markdown(page_header_html(
            "Survival Analysis",
            "Kaplan–Meier estimation, log-rank testing, and Cox proportional hazards regression.",
            dataset_label=f"{st.session_state.dataset_name} &middot; {len(df):,} records"
        ), unsafe_allow_html=True)

        time_col  = cm.get("time", "follow_up_months")
        event_col = cm.get("event", "event")
        alpha     = st.session_state.alpha

        if not time_col or time_col not in df.columns:
            st.error("No follow-up time column mapped.")
            st.stop()
        if not event_col or event_col not in df.columns:
            st.error("No event indicator column mapped.")
            st.stop()

        time_unit = st.selectbox("Time unit", ["months", "years", "days"], index=0)
        st.session_state.time_unit = time_unit

        # Follow-up distribution
        with st.container(border=True):
            st.markdown(card_header_html("Follow-Up Duration Distribution", "⏱️"), unsafe_allow_html=True)
            st.plotly_chart(_theme_fig(plot_follow_up_distribution(df, time_col, event_col)), use_container_width=True)

        # Overall KM
        with st.container(border=True):
            st.markdown(card_header_html("Overall Kaplan–Meier Survival Curve", "📈"), unsafe_allow_html=True)
            with st.spinner("Fitting KM..."):
                kmf_overall = fit_kaplan_meier(df, time_col, event_col, label="Overall", alpha=alpha)
                overall_sum = km_summary(kmf_overall)
                st.plotly_chart(_theme_fig(plot_kaplan_meier({"Overall": kmf_overall}, time_unit=time_unit)), use_container_width=True)
                med = overall_sum.get("median_survival")
                km1, km2, km3 = st.columns(3)
                km1.metric("Patients", f"{overall_sum['n_subjects']:,}")
                km2.metric("Events", f"{overall_sum['n_events']:,}")
                km3.metric("Median Survival", "Not reached" if med is None else f"{med:.1f} {time_unit}")

        # Group KM
        with st.container(border=True):
            st.markdown(card_header_html("Kaplan–Meier by Group & Log-Rank Test", "👥"), unsafe_allow_html=True)
            cat_cols = df.select_dtypes(include="object").columns.tolist()
            if "age_group" in df.columns:
                cat_cols = ["age_group"] + [c for c in cat_cols if c != "age_group"]
            grp_col = st.selectbox("Stratify by", cat_cols, key="km_grp")

            if grp_col:
                with st.spinner("Fitting group KM curves..."):
                    fitters = km_by_group(df, time_col, event_col, grp_col, alpha=alpha)
                    if fitters:
                        st.plotly_chart(
                            _theme_fig(plot_kaplan_meier(fitters, f"Kaplan–Meier by {grp_col}", time_unit)),
                            use_container_width=True
                        )
                        max_t = float(df[time_col].max())
                        risk_times = [round(max_t * p, 1) for p in [0, 0.25, 0.5, 0.75, 1.0]]
                        st.plotly_chart(_theme_fig(plot_at_risk_table(fitters, risk_times)), use_container_width=True)

                        lr = log_rank_test(df.dropna(subset=[time_col, event_col, grp_col]),
                                           time_col, event_col, grp_col, alpha)
                        sig = lr.get("significant", False)
                        sig_badge = '<span class="sig-yes">✓ Significant</span>' if sig else '<span class="sig-no">✗ Not significant</span>'
                        st.markdown(
                            f"**Log-Rank Test:** χ²({lr.get('df','?')}) = {lr.get('statistic',0):.3f}, "
                            f"p = {lr.get('p_value',1):.4f} {sig_badge}",
                            unsafe_allow_html=True
                        )
                        st.info(lr.get("interpretation", ""))

                        km_sums = [km_summary(f) for f in fitters.values()]
                        st.session_state.km_fitters = fitters
                        for s in km_sums:
                            st.caption(interpret_km_result(s, grp_col))

        # Cox regression
        with st.container(border=True):
            st.markdown(card_header_html("Cox Proportional Hazards Regression", "🔬"), unsafe_allow_html=True)
            all_cols = [c for c in df.columns if c not in [time_col, event_col]]
            cox_covs = st.multiselect(
                "Select covariates",
                all_cols,
                default=[c for c in ["age", "sex", "stage"] if c in all_cols]
            )
            if cox_covs and st.button("▶ Fit Cox Model", type="primary"):
                with st.spinner("Fitting Cox model..."):
                    cox_res = fit_cox(df, time_col, event_col, cox_covs, alpha)
                    st.session_state.cox_result = cox_res
                    if "error" in cox_res:
                        st.error(cox_res["error"])
                    else:
                        cx1, cx2, cx3 = st.columns(3)
                        cx1.metric("C-index", f"{cox_res['concordance_index']:.3f}")
                        cx2.metric("Patients", cox_res["n"])
                        cx3.metric("Events", cox_res["n_events"])
                        cox_tbl = cox_summary_table(cox_res)
                        st.dataframe(cox_tbl, use_container_width=True)
                        idx_col = "covariate" if "covariate" in cox_tbl.columns else cox_tbl.columns[0]
                        st.plotly_chart(_theme_fig(plot_cox_forest(cox_tbl.set_index(idx_col))), use_container_width=True)
                        st.info(interpret_cox_result(cox_res))

    # ════════════════════════════════════════════
    # PAGE: REPORTS
    # ════════════════════════════════════════════
    elif page == "Reports":
        st.markdown(page_header_html(
            "Findings & Reports",
            "Auto-generated research summary, export options, and reproducibility record.",
            dataset_label=f"{st.session_state.dataset_name} &middot; {len(df):,} records"
        ), unsafe_allow_html=True)

        alpha     = st.session_state.alpha
        out_col   = cm.get("outcome") or cm.get("event")
        out_sum   = {}
        if out_col and out_col in df.columns:
            out_sum = outcome_summary(df, out_col, event_value=1, alpha=alpha)
            st.session_state.outcome_sum = out_sum

        test_results = st.session_state.test_results
        cox_result   = st.session_state.cox_result
        km_fitters   = st.session_state.km_fitters
        km_sums      = [km_summary(f) for f in km_fitters.values()] if km_fitters else []

        findings = generate_findings_summary(out_sum, test_results, km_sums, cox_result)
        st.session_state.findings_text = findings

        # Findings
        with st.container(border=True):
            st.markdown(card_header_html("Synthesized Clinical Findings", "📝"), unsafe_allow_html=True)
            st.markdown(findings)

        # Limitations
        limitations = (
            "- This analysis uses observational data; causal inference is not supported.\n"
            "- Synthetic data does not represent any real patient population.\n"
            "- Unadjusted comparisons may be confounded by unmeasured clinical variables.\n"
            "- Missing data may introduce bias if not missing completely at random (MCAR).\n"
            "- The log-rank test assumes non-informative right censoring.\n"
            "- Cox model results rely on the proportional hazards assumption holding over time.\n"
            "- Small subgroup sizes reduce statistical power and widen confidence intervals.\n"
            "- Results apply specifically to the observed cohort and follow-up window."
        )
        with st.container(border=True):
            st.markdown(card_header_html("Methodological Limitations", "⚠️"), unsafe_allow_html=True)
            st.markdown(limitations)

        # Methodology
        with st.expander("📖 Statistical Methodology Reference"):
            st.markdown("""
**Test selection logic:**
- Binary outcome, 2 groups, adequate counts → Two-proportion z-test
- Binary outcome, 2 groups, sparse counts → Fisher's exact test
- Binary outcome, multiple groups → Chi-square test
- Numeric outcome, 2 groups → Welch's t-test
- Numeric outcome, multiple groups → Kruskal-Wallis H-test
- Survival curves → Log-rank test
- Multivariable survival → Cox proportional hazards

**Confidence intervals:** Wilson score (proportions), t-distribution (means), profile likelihood (Cox HRs).

**Multiple testing:** Holm step-down procedure (default); Benjamini-Hochberg FDR available.

**Censoring:** Right-censoring handled correctly in KM and Cox models. Non-informative censoring assumed.
""")

        # Reproducibility
        rep_record = build_reproducibility_record(
            dataset_name=st.session_state.dataset_name,
            dataset_source=st.session_state.dataset_source,
            column_mapping=cm,
            preprocessing_settings={"drop_duplicates": True, "drop_missing_outcome": True},
            analysis_settings={"alpha": alpha, "time_unit": st.session_state.time_unit},
            random_seed=RANDOM_SEED,
        )
        rep_text = reproducibility_to_text(rep_record)
        with st.expander("🔁 Reproducibility & Provenance Record"):
            st.code(rep_text)

        # Downloads
        with st.container(border=True):
            st.markdown(card_header_html("Export Datasets & Results (CSV)", "💾"), unsafe_allow_html=True)
            dl1, dl2, dl3 = st.columns(3)
            with dl1:
                st.download_button(
                    "⬇️ Analytical Dataset (CSV)",
                    df.to_csv(index=False).encode(),
                    "analytical_dataset.csv", "text/csv",
                    use_container_width=True
                )
            with dl2:
                if test_results:
                    res_df = pd.DataFrame([{
                        "test": r.get("test_name",""), "n": r.get("n",""),
                        "statistic": r.get("statistic",""), "p_value": r.get("p_value",""),
                        "effect_size": r.get("effect_size",""), "significant": r.get("significant","")
                    } for r in test_results])
                    st.download_button(
                        "⬇️ Test Results (CSV)",
                        res_df.to_csv(index=False).encode(),
                        "test_results.csv", "text/csv",
                        use_container_width=True
                    )
                else:
                    st.button("⬇️ Test Results (CSV)", disabled=True, use_container_width=True,
                              help="Run hypothesis tests first.")
            with dl3:
                if cox_result and "error" not in cox_result:
                    st.download_button(
                        "⬇️ Cox Results (CSV)",
                        cox_summary_table(cox_result).to_csv(index=False).encode(),
                        "cox_results.csv", "text/csv",
                        use_container_width=True
                    )
                else:
                    st.button("⬇️ Cox Results (CSV)", disabled=True, use_container_width=True,
                              help="Fit Cox model first.")

        # Preprocessing log download
        if st.session_state.prep_log:
            log_df = st.session_state.prep_log.to_dataframe()
            st.download_button(
                "⬇️ Download Preprocessing Audit Log (CSV)",
                log_df.to_csv(index=False).encode(),
                "preprocessing_log.csv", "text/csv"
            )

        # PDF report
        with st.container(border=True):
            st.markdown(card_header_html("Export Official Research Report (PDF)", "📄"), unsafe_allow_html=True)
            st.caption("Generates a comprehensive publication-ready PDF report including executive findings, statistics, charts, limitations, and reproducibility metadata.")
            if st.button("📄 Generate PDF Report", type="primary"):
                with st.spinner("Compiling and generating PDF report..."):
                    try:
                        os.makedirs(REPORT_DIR, exist_ok=True)
                        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        pdf_path = os.path.join(REPORT_DIR, f"survival_report_{ts}.pdf")
                        num_sum = numeric_summary(df)
                        prep_log_df = st.session_state.prep_log.to_dataframe() if st.session_state.prep_log else pd.DataFrame()
                        generate_pdf_report(
                            output_path=pdf_path,
                            dataset_name=st.session_state.dataset_name,
                            dataset_source=st.session_state.dataset_source,
                            dataset_description=(
                                "Synthetic dataset generated for development and testing. Not real clinical data."
                                if "Synthetic" in st.session_state.dataset_name else "User-uploaded dataset."
                            ),
                            preprocessing_log=prep_log_df,
                            numeric_summary=num_sum,
                            outcome_summary=out_sum,
                            test_results=test_results,
                            km_summaries=km_sums if km_sums else None,
                            cox_result=cox_result,
                            findings_text=findings,
                            limitations_text=limitations,
                            reproducibility_text=rep_text,
                        )
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                "⬇️ Download Generated PDF",
                                f.read(),
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf",
                                use_container_width=True
                            )
                        st.success(f"Report successfully saved to {pdf_path}")
                    except Exception as e:
                        st.error(f"PDF generation failed: {e}")
                        logger.exception("PDF error")

    # ── Global Unified Footer ───────────────────────────────────────────────
    st.markdown(footer_html(), unsafe_allow_html=True)
