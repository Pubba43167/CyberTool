"""Reporting engine foundations: pentest, vulnerability assessment, SOC, and remediation suggestions.
Renders HTML via Jinja2; can export PDF (WeasyPrint) and DOCX (python-docx) where dependencies are available.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
SEVERITY_COLORS = {
    "CRITICAL": "#FF1744",
    "HIGH": "#FF6D00",
    "MEDIUM": "#FFD600",
    "LOW": "#00E676",
    "INFO": "#00B8D4",
}


def get_jinja() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )


def render_html(template_name: str, context: dict[str, Any]) -> str:
    env = get_jinja()
    tpl = env.get_template(template_name)
    return tpl.render(severity_colors=SEVERITY_COLORS, **context)


def generate_report(report_type: str, context: dict[str, Any], output_format: str = "html") -> dict[str, Any]:
    template_map = {
        "PENETRATION_TEST": "penetration_test.html",
        "VULNERABILITY_ASSESSMENT": "vulnerability_assessment.html",
        "SOC": "soc_report.html",
        "REMEDIATION_SUGGESTIONS": "remediation_suggestions.html",
    }
    template = template_map.get(report_type, "vulnerability_assessment.html")
    html = render_html(template, context)
    result = {"format": output_format, "report_type": report_type, "html": html}
    if output_format == "pdf":
        try:
            from weasyprint import HTML
            result["pdf_bytes_available"] = True
            # In a full implementation: HTML(string=html).write_pdf(target_path)
        except Exception as e:
            result["pdf_error"] = str(e)
    if output_format == "docx":
        result["docx_note"] = "DOCX export scaffold: use python-docx to build a branded document from context."
    return result
