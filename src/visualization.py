"""Visualization: Plotly charts for EDA, hypothesis testing, and survival analysis."""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from lifelines import KaplanMeierFitter


# ---------------------------------------------------------------------------
# EDA charts
# ---------------------------------------------------------------------------

def plot_histogram(df: pd.DataFrame, col: str, title: str | None = None, nbins: int = 30) -> go.Figure:
    fig = px.histogram(
        df, x=col, nbins=nbins,
        title=title or f"Distribution of {col}",
        labels={col: col},
        template="plotly_white",
    )
    fig.update_layout(bargap=0.05, xaxis_title=col, yaxis_title="Count")
    return fig


def plot_boxplot(df: pd.DataFrame, y_col: str, x_col: str | None = None, title: str | None = None) -> go.Figure:
    fig = px.box(
        df, x=x_col, y=y_col,
        title=title or f"Box Plot: {y_col}" + (f" by {x_col}" if x_col else ""),
        template="plotly_white",
        points="outliers",
    )
    return fig


def plot_bar(df: pd.DataFrame, col: str, title: str | None = None) -> go.Figure:
    vc = df[col].value_counts().reset_index()
    vc.columns = [col, "Count"]
    fig = px.bar(
        vc, x=col, y="Count",
        title=title or f"Frequency: {col}",
        template="plotly_white",
        text="Count",
    )
    fig.update_traces(textposition="outside")
    return fig


def plot_missing_heatmap(df: pd.DataFrame) -> go.Figure:
    missing_pct = (df.isnull().mean() * 100).reset_index()
    missing_pct.columns = ["Column", "Missing %"]
    missing_pct = missing_pct[missing_pct["Missing %"] > 0].sort_values("Missing %", ascending=False)
    if missing_pct.empty:
        fig = go.Figure()
        fig.add_annotation(text="No missing values detected.", showarrow=False, font_size=14)
        return fig
    fig = px.bar(
        missing_pct, x="Column", y="Missing %",
        title="Missing Values by Column (%)",
        template="plotly_white",
        color="Missing %",
        color_continuous_scale="Reds",
    )
    return fig


def plot_outcome_pie(n_event: int, n_nonevent: int, event_label: str = "Event", nonevent_label: str = "No Event") -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=[event_label, nonevent_label],
        values=[n_event, n_nonevent],
        hole=0.35,
        textinfo="label+percent+value",
    ))
    fig.update_layout(title="Outcome Distribution", template="plotly_white")
    return fig


def plot_group_proportions(summary_df: pd.DataFrame, group_col: str = "group") -> go.Figure:
    """Bar chart of event proportions with error bars (Wilson CI)."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=summary_df[group_col].astype(str),
        y=summary_df["proportion"],
        error_y=dict(
            type="data",
            symmetric=False,
            array=(summary_df["ci_upper"] - summary_df["proportion"]).tolist(),
            arrayminus=(summary_df["proportion"] - summary_df["ci_lower"]).tolist(),
        ),
        text=(summary_df["proportion"] * 100).round(1).astype(str) + "%",
        textposition="outside",
    ))
    fig.update_layout(
        title="Event Proportion by Group (with 95% Wilson CI)",
        xaxis_title=group_col,
        yaxis_title="Proportion",
        yaxis_range=[0, 1],
        template="plotly_white",
    )
    return fig


def plot_correlation_heatmap(df: pd.DataFrame, cols: list[str] | None = None) -> go.Figure:
    num_df = df[cols] if cols else df.select_dtypes(include="number")
    corr = num_df.corr()
    fig = px.imshow(
        corr, text_auto=".2f", aspect="auto",
        title="Correlation Matrix",
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        template="plotly_white",
    )
    return fig


# ---------------------------------------------------------------------------
# Survival charts
# ---------------------------------------------------------------------------

def plot_kaplan_meier(
    fitters: dict[str, KaplanMeierFitter],
    title: str = "Kaplan-Meier Survival Curves",
    time_unit: str = "months",
    show_ci: bool = True,
) -> go.Figure:
    """
    Plot Kaplan-Meier survival curves for one or more groups.

    Parameters
    ----------
    fitters : dict mapping group label -> fitted KaplanMeierFitter
    """
    fig = go.Figure()
    colors = px.colors.qualitative.Set1

    for i, (label, kmf) in enumerate(fitters.items()):
        sf = kmf.survival_function_
        t = sf.index.tolist()
        s = sf.iloc[:, 0].tolist()
        color = colors[i % len(colors)]

        fig.add_trace(go.Scatter(
            x=t, y=s, mode="lines", name=label,
            line=dict(color=color, width=2),
        ))

        if show_ci:
            ci = kmf.confidence_interval_survival_function_
            lo = ci.iloc[:, 0].tolist()
            hi = ci.iloc[:, 1].tolist()
            fig.add_trace(go.Scatter(
                x=t + t[::-1], y=hi + lo[::-1],
                fill="toself", fillcolor=color,
                opacity=0.15, line=dict(width=0),
                showlegend=False, name=f"{label} CI",
            ))

    fig.update_layout(
        title=title,
        xaxis_title=f"Time ({time_unit})",
        yaxis_title="Survival Probability",
        yaxis_range=[0, 1.05],
        template="plotly_white",
        legend_title="Group",
    )
    return fig


def plot_at_risk_table(
    fitters: dict[str, KaplanMeierFitter],
    time_points: list[float],
) -> go.Figure:
    """Create a numbers-at-risk table as a Plotly figure."""
    rows = []
    for label, kmf in fitters.items():
        et = kmf.event_table
        for t in time_points:
            idx = et.index[et.index <= t]
            at_risk = int(et.loc[idx[-1], "at_risk"]) if len(idx) else 0
            rows.append({"Group": label, "Time": t, "At Risk": at_risk})
    df = pd.DataFrame(rows)
    if df.empty:
        return go.Figure()
    pivot = df.pivot(index="Group", columns="Time", values="At Risk").fillna(0).astype(int)
    fig = go.Figure(go.Table(
        header=dict(values=["Group"] + [str(t) for t in time_points], fill_color="lightgrey"),
        cells=dict(values=[pivot.index.tolist()] + [pivot[t].tolist() for t in time_points]),
    ))
    fig.update_layout(title="Numbers at Risk", template="plotly_white")
    return fig


def plot_cox_forest(cox_summary: pd.DataFrame) -> go.Figure:
    """Forest plot of Cox model hazard ratios."""
    if "HR" not in cox_summary.columns:
        return go.Figure()
    df = cox_summary.dropna(subset=["HR"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["HR"], y=df.index.astype(str),
        mode="markers",
        marker=dict(size=10, color="steelblue"),
        error_x=dict(
            type="data", symmetric=False,
            array=(df["HR_upper"] - df["HR"]).tolist(),
            arrayminus=(df["HR"] - df["HR_lower"]).tolist(),
        ),
        name="HR (95% CI)",
    ))
    fig.add_vline(x=1.0, line_dash="dash", line_color="red", annotation_text="HR = 1")
    fig.update_layout(
        title="Cox Model: Hazard Ratios (95% CI)",
        xaxis_title="Hazard Ratio",
        yaxis_title="Covariate",
        template="plotly_white",
        xaxis_type="log",
    )
    return fig


def plot_follow_up_distribution(df: pd.DataFrame, time_col: str, event_col: str) -> go.Figure:
    """Histogram of follow-up times, coloured by event/censored status."""
    plot_df = df[[time_col, event_col]].dropna().copy()
    plot_df["Status"] = plot_df[event_col].map({1: "Event", 0: "Censored"}).fillna("Unknown")
    fig = px.histogram(
        plot_df, x=time_col, color="Status",
        barmode="overlay", nbins=40,
        title="Follow-Up Duration Distribution",
        labels={time_col: "Follow-Up Time"},
        template="plotly_white",
        opacity=0.7,
    )
    return fig
