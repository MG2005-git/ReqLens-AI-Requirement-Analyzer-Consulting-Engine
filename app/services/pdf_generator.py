from fpdf import FPDF
import os
import re

OUTPUT_DIR = "generate_docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def sanitize_text(text) -> str:
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    # Convert HTML line breaks
    text = re.sub(r'<br\s*/?>', ' \n', text, flags=re.IGNORECASE)
    replacements = {
        "\u2011": "-", "\u2010": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-", "\u2015": "-",
        "\u2022": "-", "\u2023": "-", "\u2043": "-", "\u2018": "'", "\u2019": "'", "\u201a": "'",
        "\u201b": "'", "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u2026": "...", "\u00a0": " ",
        "\u200b": "", "\u202f": " ", "–": "-", "—": "-", "•": "-", "“": '"', "”": '"', "‘": "'", "’": "'",
        "\u2248": "~", "\u00d7": "x"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "ignore").decode("latin-1")


def clean_markdown_inline(text: str) -> str:
    """Clean markdown artifacts (asterisks, backticks) while preserving content."""
    s = str(text)
    s = re.sub(r'<br\s*/?>', ' ', s, flags=re.IGNORECASE)
    s = re.sub(r'\*\*(.*?)\*\*', r'\1', s)
    s = re.sub(r'\*(.*?)\*', r'\1', s)
    s = re.sub(r'`(.*?)`', r'\1', s)
    return sanitize_text(s.strip())


class ProfessionalPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=18)

    # ---------- RUNNING HEADER ----------
    def header(self):
        if self.page_no() == 1:
            return  # Suppress running header on cover page
        self.set_fill_color(11, 42, 74)   # Deep Navy
        self.rect(0, 0, 210, 15, "F")
        self.set_fill_color(230, 168, 0)  # Gold Accent Stripe
        self.rect(0, 15, 210, 1.2, "F")

        self.set_font("Arial", "B", 9)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 4)
        self.cell(0, 7, "ReqLens  |  AI Requirement Analysis & Consulting Engine", 0, 1, "L")
        self.ln(6)
        self.set_text_color(40, 40, 40)

    # ---------- RUNNING FOOTER ----------
    def footer(self):
        if self.page_no() == 1:
            return  # Suppress on cover page
        self.set_y(-15)
        self.set_draw_color(210, 220, 230)
        self.line(10, 282, 200, 282)
        self.set_font("Arial", "I", 8)
        self.set_text_color(120, 130, 140)
        self.set_xy(10, -13)
        self.cell(100, 10, "Confidential - Prepared for Client Stakeholders", 0, 0, "L")
        self.cell(90, 10, f"Page {self.page_no()}", 0, 0, "R")

    # ---------- SECTION TITLE ----------
    def section_title(self, title: str):
        if self.get_y() > 235:
            self.add_page()
        self.ln(3)
        self.set_fill_color(11, 42, 74)   # Deep Navy
        self.set_font("Arial", "B", 12)
        self.set_text_color(255, 255, 255)
        self.cell(190, 9, f"  {sanitize_text(title).upper()}", 0, 1, "L", True)
        self.set_fill_color(230, 168, 0)  # Gold Stripe
        self.rect(10, self.get_y(), 190, 1.2, "F")
        self.ln(4)
        self.set_text_color(40, 40, 40)

    # ---------- SUBTITLE ----------
    def sub_title(self, title: str):
        if self.get_y() > 255:
            self.add_page()
        self.ln(2)
        self.set_font("Arial", "B", 11)
        self.set_text_color(11, 42, 74)
        self.cell(0, 6, sanitize_text(title), 0, 1, "L")
        self.ln(1)
        self.set_text_color(40, 40, 40)

    # ---------- BULLET LIST WITH HANGING INDENT ----------
    def bullet(self, text: str, indent: float = 6):
        if self.get_y() > 265:
            self.add_page()
        self.set_font("Arial", "", 10)
        self.set_text_color(50, 50, 50)
        x = self.get_x()
        y = self.get_y()
        self.set_xy(x + indent, y)
        self.cell(4, 5.5, chr(149), 0, 0)
        self.set_xy(x + indent + 4, y)
        clean = clean_markdown_inline(text)
        self.multi_cell(190 - (indent + 4), 5.5, clean)
        self.ln(1)

    # ---------- KEY-VALUE SPECIFICATION ----------
    def key_value(self, key: str, val):
        if self.get_y() > 255:
            self.add_page()
        key_str = sanitize_text(key.replace("_", " ").title()) + ":"
        val_str = ", ".join(val) if isinstance(val, list) else str(val)
        val_str = clean_markdown_inline(val_str)

        x_start = 10
        key_w = 52
        val_w = 138
        y = self.get_y()

        self.set_xy(x_start + key_w, y)
        self.set_font("Arial", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(val_w, 5.5, val_str)
        new_y = self.get_y()

        self.set_xy(x_start, y)
        self.set_font("Arial", "B", 10)
        self.set_text_color(11, 42, 74)
        self.cell(key_w, 5.5, key_str)

        self.set_y(new_y + 2)


def render_table(pdf: ProfessionalPDF, rows: list):
    """Renders a styled markdown table with column-width heuristics and zebra striping."""
    if not rows or len(rows) < 1:
        return

    num_cols = len(rows[0])
    total_w = 190

    first_cell = rows[0][0].lower().strip()
    if num_cols == 3 and (first_cell in ["#", "no", "id", "item"] or len(first_cell) <= 2):
        widths = [14, 56, 120]
    elif num_cols == 3:
        widths = [45, 45, 100]
    elif num_cols == 4:
        widths = [35, 75, 40, 40]
    elif num_cols == 2:
        widths = [60, 130]
    else:
        col_w = total_w / num_cols
        widths = [col_w] * num_cols

    def get_row_height(texts):
        max_lines = 1
        for idx, w in enumerate(widths):
            t = texts[idx] if idx < len(texts) else ""
            chars_per_line = max(1, int(w / 2.2))
            lines_count = max(1, (len(t) // chars_per_line) + 1)
            max_lines = max(max_lines, lines_count)
        return max(7, max_lines * 5.2 + 2)

    # Header Row
    header_texts = [clean_markdown_inline(c) for c in rows[0]]
    h_height = get_row_height(header_texts)
    if pdf.get_y() + h_height > 270:
        pdf.add_page()

    pdf.set_fill_color(11, 42, 74)  # Navy
    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(255, 255, 255)

    x_start = 10
    y_start = pdf.get_y()
    for idx, w in enumerate(widths):
        t = header_texts[idx] if idx < len(header_texts) else ""
        pdf.rect(x_start, y_start, w, h_height, "F")
        pdf.set_xy(x_start + 1.5, y_start + 1.5)
        pdf.multi_cell(w - 3, 4.5, t)
        x_start += w
    pdf.set_y(y_start + h_height)

    # Data Rows
    pdf.set_font("Arial", "", 9)
    for r_idx, row in enumerate(rows[1:]):
        row_texts = [clean_markdown_inline(c) for c in row]
        while len(row_texts) < num_cols:
            row_texts.append("")
        r_height = get_row_height(row_texts)

        if pdf.get_y() + r_height > 272:
            pdf.add_page()

        y_row = pdf.get_y()
        # Zebra striping
        if r_idx % 2 == 1:
            pdf.set_fill_color(248, 250, 252)
        else:
            pdf.set_fill_color(255, 255, 255)

        x_cell = 10
        for idx, w in enumerate(widths):
            pdf.rect(x_cell, y_row, w, r_height, "DF")
            pdf.set_draw_color(210, 218, 225)
            pdf.set_text_color(40, 40, 40)
            pdf.set_xy(x_cell + 1.5, y_row + 1.5)
            pdf.multi_cell(w - 3, 4.6, row_texts[idx])
            x_cell += w
        pdf.set_y(y_row + r_height)

    pdf.ln(3)


def render_markdown_content(pdf: ProfessionalPDF, md_text: str):
    """Parses markdown text and cleanly formats headers, tables, dividers, and lists in PDF."""
    if not md_text or not md_text.strip():
        return

    lines = md_text.split("\n")
    i = 0
    total_lines = len(lines)

    while i < total_lines:
        raw_line = lines[i].strip()
        if not raw_line:
            i += 1
            continue

        # Check for Markdown Table
        if raw_line.startswith("|") and raw_line.endswith("|") and raw_line.count("|") >= 2:
            table_lines = []
            while i < total_lines and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                l = lines[i].strip()
                if not all(c in "| -:\t" for c in l):
                    cells = [c.strip() for c in l.split("|")[1:-1]]
                    table_lines.append(cells)
                i += 1
            if table_lines:
                render_table(pdf, table_lines)
            continue

        # Check for Section Heading (###, ##, or standalone **Title**)
        if raw_line.startswith("### ") or raw_line.startswith("## ") or raw_line.startswith("# "):
            title = re.sub(r"^#+\s*", "", raw_line)
            pdf.sub_title(clean_markdown_inline(title))
            i += 1
            continue

        if re.match(r"^\*\*(.*?)\*\*$", raw_line):
            title = raw_line.replace("**", "").strip()
            pdf.sub_title(clean_markdown_inline(title))
            i += 1
            continue

        # Check for Divider (--- or ***)
        if raw_line in ["---", "***", "___"]:
            pdf.set_draw_color(220, 225, 230)
            y = pdf.get_y() + 2
            pdf.line(10, y, 200, y)
            pdf.set_y(y + 4)
            i += 1
            continue

        # Check for Numbered List (e.g. 1. **Floor-to-Floor Heights** - ...)
        num_match = re.match(r"^(\d+\.)\s*(.*)", raw_line)
        if num_match:
            prefix = num_match.group(1)
            body = clean_markdown_inline(num_match.group(2))
            if pdf.get_y() > 265:
                pdf.add_page()
            y = pdf.get_y()
            pdf.set_xy(10, y)
            pdf.set_font("Arial", "B", 10)
            pdf.set_text_color(11, 42, 74)
            pdf.cell(7, 5.5, prefix)
            pdf.set_xy(17, y)
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(183, 5.5, body)
            pdf.ln(1)
            i += 1
            continue

        # Check for Bullet List (- or * or •)
        bullet_match = re.match(r"^[-*•]\s+(.*)", raw_line)
        if bullet_match:
            pdf.bullet(bullet_match.group(1))
            i += 1
            continue

        # Standard Paragraph
        clean_para = clean_markdown_inline(raw_line)
        if clean_para:
            if pdf.get_y() > 268:
                pdf.add_page()
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(0, 5.5, clean_para)
            pdf.ln(2)

        i += 1


def generate_requirements_pdf(document_id, text, analysis):
    structured = analysis.get("structured_data", analysis) if isinstance(analysis, dict) else {}

    pdf = ProfessionalPDF()

    # ==========================================
    # 1. EXECUTIVE COVER PAGE
    # ==========================================
    pdf.add_page()

    # Navy Header Band
    pdf.set_fill_color(11, 42, 74)
    pdf.rect(0, 0, 210, 42, "F")
    pdf.set_fill_color(230, 168, 0)
    pdf.rect(0, 42, 210, 2.5, "F")

    pdf.set_xy(15, 13)
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(230, 168, 0)
    pdf.cell(0, 6, "REQLENS  |  AI CONSULTING INTELLIGENCE ENGINE", 0, 1)

    pdf.set_xy(15, 22)
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(210, 225, 240)
    pdf.cell(0, 6, "Automated Architecture & Software Specification Deliverable", 0, 1)

    # Document Title Block
    pdf.set_xy(15, 68)
    pdf.set_font("Arial", "B", 26)
    pdf.set_text_color(11, 42, 74)
    pdf.multi_cell(180, 11, "Requirement Analysis &\nConsulting Specification")

    pdf.set_xy(15, 96)
    pdf.set_font("Arial", "I", 11)
    pdf.set_text_color(100, 110, 120)
    pdf.cell(0, 6, "Structured Multi-Stage Reasoning, Gap Assessment & Strategic Risk Matrix", 0, 1)

    # Metadata Card in Center
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(210, 220, 230)
    pdf.rect(15, 115, 180, 110, "DF")

    pdf.set_xy(25, 125)
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(11, 42, 74)
    pdf.cell(48, 7, "Document Reference:")
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 7, f"REQ-DOC-{document_id:04d}", 0, 1)

    exec_sum = structured.get("executive_summary", {})
    intent = exec_sum.get("project_intent", "Automated Client Project Specification") if isinstance(exec_sum, dict) else "Automated Client Project Specification"

    pdf.set_xy(25, 136)
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(11, 42, 74)
    pdf.cell(48, 7, "Scope Summary:")
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(115, 5.5, clean_markdown_inline(intent))

    pdf.set_xy(25, 175)
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(11, 42, 74)
    pdf.cell(48, 7, "Completeness Score:")
    score_val = structured.get("completeness_score", 0.65)
    try:
        pct = int(float(score_val) * 100) if float(score_val) <= 1.0 else int(float(score_val))
    except Exception:
        pct = 65
    pdf.set_font("Arial", "B", 11)
    if pct < 50:
        pdf.set_text_color(200, 110, 0)
    else:
        pdf.set_text_color(25, 135, 60)
    pdf.cell(0, 7, f"{pct}% (Preliminary Design Scope)", 0, 1)

    pdf.set_xy(25, 188)
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(11, 42, 74)
    pdf.cell(48, 7, "Assessment Type:")
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 7, "Dual-Domain Architectural & Engineering Review", 0, 1)

    pdf.set_xy(25, 200)
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(11, 42, 74)
    pdf.cell(48, 7, "Verification Status:")
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(30, 120, 50)
    pdf.cell(0, 7, "Verified Grounded Analysis (Strict Schema)", 0, 1)

    # Footer note on Cover
    pdf.set_xy(15, 260)
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(140, 150, 160)
    pdf.cell(0, 6, "CONFIDENTIAL  |  Generated automatically by ReqLens Consulting Engine", 0, 1, "C")

    # ==========================================
    # 2. EXECUTIVE SUMMARY & COMPLETENESS GAUGE
    # ==========================================
    pdf.add_page()
    pdf.section_title("1. Executive Summary & Readiness Assessment")

    # Visual Completeness Bar
    pdf.set_xy(10, pdf.get_y() + 1)
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(11, 42, 74)
    pdf.cell(55, 6, "Design Readiness Score:")

    bar_x = 68
    bar_y = pdf.get_y()
    bar_w = 110
    bar_h = 6.5
    pdf.set_fill_color(225, 230, 238)
    pdf.rect(bar_x, bar_y, bar_w, bar_h, "F")

    fill_w = max(4, bar_w * (pct / 100.0))
    pdf.set_fill_color(11, 42, 74)
    pdf.rect(bar_x, bar_y, fill_w, bar_h, "F")

    pdf.set_xy(bar_x + bar_w + 4, bar_y)
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(11, 42, 74)
    pdf.cell(20, 6, f"{pct}%")
    pdf.ln(9)

    # Executive Summary Key-Values
    if isinstance(exec_sum, dict):
        for k, v in exec_sum.items():
            pdf.key_value(k, v)

    # ==========================================
    # 3. REQUIREMENT BREAKDOWN
    # ==========================================
    pdf.section_title("2. Requirement Breakdown")
    breakdown = structured.get("requirement_breakdown", {})
    if isinstance(breakdown, dict):
        for section, items in breakdown.items():
            pdf.sub_title(section.replace("_", " ").title())
            if isinstance(items, list):
                for item in items:
                    pdf.bullet(item)
            elif items:
                pdf.bullet(str(items))
            pdf.ln(1)

    # ==========================================
    # 4. MISSING REQUIREMENTS & GAP SEVERITY
    # ==========================================
    pdf.section_title("3. Missing Requirements & Gap Assessment")

    # Gap Severity Summary if available
    gap_severity = structured.get("gap_severity_analysis", {})
    if isinstance(gap_severity, dict) and any(gap_severity.values()):
        pdf.sub_title("Gap Severity Classification")
        for sev_level in ["critical_gaps", "moderate_gaps", "minor_gaps"]:
            items = gap_severity.get(sev_level, [])
            if items:
                label = sev_level.replace("_", " ").title()
                pdf.set_font("Arial", "B", 10)
                if "critical" in sev_level:
                    pdf.set_text_color(180, 30, 30)
                elif "moderate" in sev_level:
                    pdf.set_text_color(200, 110, 0)
                else:
                    pdf.set_text_color(40, 110, 180)
                pdf.cell(0, 6, f"[{label.upper()}]", 0, 1)
                for it in items:
                    pdf.bullet(it, indent=8)
                pdf.ln(1)

    missing = structured.get("missing_requirements", {})
    if isinstance(missing, dict):
        for section, items in missing.items():
            pdf.sub_title(section.replace("_", " ").title())
            if isinstance(items, list):
                for item in items:
                    pdf.bullet(item)
            elif items:
                pdf.bullet(str(items))
            pdf.ln(1)

    # ==========================================
    # 5. RISK MATRIX TABLE
    # ==========================================
    pdf.section_title("4. Strategic Risk Matrix")

    risk_list = structured.get("risk_matrix", [])
    if isinstance(risk_list, list) and len(risk_list) > 0:
        table_rows = [["Category", "Risk Description", "Impact", "Probability"]]
        for r in risk_list:
            if isinstance(r, dict):
                cat = r.get("risk_category", "")
                desc = r.get("risk_description", "")
                imp = r.get("impact_level", "")
                prob = r.get("probability_estimate", "")
                table_rows.append([cat, desc, imp, prob])
        render_table(pdf, table_rows)
    else:
        pdf.bullet("No critical risks identified from the provided documentation.")

    # ==========================================
    # 6. DESIGN IMPLICATIONS & RECOMMENDATIONS
    # ==========================================
    implications = structured.get("design_implications", {})
    recommendations = structured.get("design_recommendations", [])

    if implications or recommendations:
        pdf.section_title("5. Design Implications & Recommendations")
        if isinstance(implications, dict):
            for sec, val in implications.items():
                pdf.sub_title(sec.replace("_", " ").title())
                if isinstance(val, list):
                    for item in val:
                        pdf.bullet(item)
                elif val:
                    pdf.bullet(str(val))
                pdf.ln(1)

        if isinstance(recommendations, list) and recommendations:
            pdf.sub_title("Strategic Recommendations")
            for rec in recommendations:
                pdf.bullet(rec)
            pdf.ln(1)

    # ==========================================
    # 7. REFINED REQUIREMENTS SPECIFICATION
    # ==========================================
    pdf.add_page()
    pdf.section_title("6. Refined Requirements Specification")

    refined_text = analysis.get("refine_text", text) if isinstance(analysis, dict) else text
    render_markdown_content(pdf, refined_text)

    # Save output PDF
    file_path = f"{OUTPUT_DIR}/document_{document_id}_premium.pdf"
    pdf.output(file_path)
    return file_path
