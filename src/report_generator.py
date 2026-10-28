"""PDF report generation using ReportLab."""

from __future__ import annotations

import datetime
import io
import logging
import os
from typing import Optional

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
    Table, TableStyle, PageBreak, HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

logger = logging.getLogger(__name__)

W, H = A4
MARGIN = 2 * cm


def _styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("CentreTitle", parent=s["Title"], alignment=TA_CENTER, fontSize=20, spaceAfter=12))
    s.add(ParagraphStyle("SectionHead", parent=s["Heading1"], fontSize=13, spaceBefore=14, spaceAfter=6))
    s.add(ParagraphStyle("SubHead", parent=s["Heading2"], fontSize=11, spaceBefore=10, spaceAfter=4))
    s.add(ParagraphStyle("Body", parent=s["Normal"], fontSize=9, leading=14, alignment=TA_JUSTIFY))
    s.add(ParagraphStyle("Small", parent=s["Normal"], fontSize=8, leading=12))
    s.add(ParagraphStyle("Caption", parent=s["Normal"], fontSize=8, textColor=colors.grey, alignment=TA_CENTER))
    return s


def _header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(MARGIN, 1.2 * cm, "Comparative Statistical Analysis of Patient Survival Rates")
    canvas.drawRightString(W - MARGIN, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def _df_to_table(df: pd.DataFrame, col_widths=None, max_rows: int = 50) -> Table:
    df_show = df.head(max_rows)
    data = [df_show.columns.tolist()] + df_show.astype(str).values.tolist()
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def generate_pdf_report(
    output_path: str,
    dataset_name: str,
    dataset_source: str,
    dataset_description: str,
    preprocessing_log: pd.DataFrame,
    numeric_summary: pd.DataFrame,
    outcome_summary: dict,
    test_results: list[dict],
    km_summaries: list[dict] | None,
    cox_result: dict | None,
    findings_text: str,
    limitations_text: str,
    reproducibility_text: str,
    data_dict: pd.DataFrame | None = None,
) -> str:
    """
    Generate a PDF report and save to output_path.

    Returns the output path on success.
    """
    S = _styles()
    story = []

    # ---- Title page ----
    story += [
        Spacer(1, 3 * cm),
        Paragraph("Comparative Statistical Analysis of", S["CentreTitle"]),
        Paragraph("Patient Survival Rates", S["CentreTitle"]),
        Spacer(1, 0.5 * cm),
        HRFlowable(width="80%", thickness=1, color=colors.HexColor("#2c3e50")),
        Spacer(1, 0.5 * cm),
        Paragraph(f"Dataset: {dataset_name}", S["Body"]),
        Paragraph(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", S["Body"]),
        PageBreak(),
    ]

    # ---- Executive summary ----
    story += [
        Paragraph("Executive Summary", S["SectionHead"]),
        Paragraph(findings_text.replace("\n\n", "<br/><br/>"), S["Body"]),
        Spacer(1, 0.4 * cm),
    ]

    # ---- Dataset ----
    story += [
        Paragraph("Dataset Description", S["SectionHead"]),
        Paragraph(f"<b>Name:</b> {dataset_name}", S["Body"]),
        Paragraph(f"<b>Source:</b> {dataset_source}", S["Body"]),
        Paragraph(dataset_description, S["Body"]),
        Spacer(1, 0.3 * cm),
    ]

    if data_dict is not None and not data_dict.empty:
        story += [
            Paragraph("Data Dictionary", S["SubHead"]),
            _df_to_table(data_dict),
            Spacer(1, 0.3 * cm),
        ]

    # ---- Preprocessing ----
    story += [
        Paragraph("Data Quality and Preprocessing", S["SectionHead"]),
        _df_to_table(preprocessing_log),
        Spacer(1, 0.3 * cm),
    ]

    # ---- Descriptive statistics ----
    story += [
        Paragraph("Descriptive Statistics", S["SectionHead"]),
        _df_to_table(numeric_summary),
        Spacer(1, 0.3 * cm),
    ]

    # ---- Outcome summary ----
    story += [
        Paragraph("Outcome Summary", S["SectionHead"]),
        Paragraph(
            f"Total patients: {outcome_summary.get('n_total', 'N/A')} | "
            f"Events: {outcome_summary.get('n_event', 'N/A')} "
            f"({outcome_summary.get('proportion', 0):.1%}) | "
            f"95% CI: {outcome_summary.get('ci_lower', 0):.1%}–{outcome_summary.get('ci_upper', 0):.1%}",
            S["Body"],
        ),
        Spacer(1, 0.3 * cm),
    ]

    # ---- Hypothesis tests ----
    story.append(Paragraph("Hypothesis Testing Results", S["SectionHead"]))
    for i, r in enumerate(test_results, 1):
        story += [
            Paragraph(f"Test {i}: {r.get('test_name', '')}", S["SubHead"]),
            Paragraph(f"<b>H₀:</b> {r.get('h0', '')}", S["Body"]),
            Paragraph(f"<b>H₁:</b> {r.get('h1', '')}", S["Body"]),
            Paragraph(
                f"n = {r.get('n', 'N/A')} | "
                f"Statistic = {r.get('statistic', 'N/A')} | "
                f"p = {r.get('p_value', 'N/A')} | "
                f"{r.get('effect_label', 'Effect')} = {r.get('effect_size', 'N/A')}",
                S["Body"],
            ),
            Paragraph(r.get("interpretation", ""), S["Body"]),
            Spacer(1, 0.2 * cm),
        ]

    # ---- Survival analysis ----
    if km_summaries:
        story.append(Paragraph("Survival Analysis", S["SectionHead"]))
        for km in km_summaries:
            med = km.get("median_survival")
            story.append(Paragraph(
                f"Group '{km.get('label', '')}': n={km.get('n_subjects', 'N/A')}, "
                f"events={km.get('n_events', 'N/A')}, "
                f"median survival={'Not reached' if med is None else f'{med:.1f} time units'}",
                S["Body"],
            ))
        story.append(Spacer(1, 0.3 * cm))

    if cox_result and "error" not in cox_result:
        story += [
            Paragraph("Cox Proportional Hazards Model", S["SubHead"]),
            Paragraph(
                f"n = {cox_result.get('n', 'N/A')}, events = {cox_result.get('n_events', 'N/A')}, "
                f"C-index = {cox_result.get('concordance_index', 'N/A')}",
                S["Body"],
            ),
            _df_to_table(cox_result["summary"].reset_index()),
            Spacer(1, 0.3 * cm),
        ]

    # ---- Limitations ----
    story += [
        Paragraph("Limitations", S["SectionHead"]),
        Paragraph(limitations_text.replace("\n", "<br/>"), S["Body"]),
        Spacer(1, 0.3 * cm),
    ]

    # ---- Reproducibility ----
    story += [
        Paragraph("Reproducibility", S["SectionHead"]),
        Paragraph(reproducibility_text.replace("\n", "<br/>"), S["Small"]),
    ]

    # Build PDF
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    doc = BaseDocTemplate(
        output_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=2 * cm,
    )
    frame = Frame(MARGIN, 2 * cm, W - 2 * MARGIN, H - 3 * cm, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=_header_footer)])
    doc.build(story)
    logger.info("PDF report saved: %s", output_path)
    return output_path


def export_csv(df: pd.DataFrame, path: str) -> str:
    df.to_csv(path, index=False)
    return path
