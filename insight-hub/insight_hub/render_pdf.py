from datetime import datetime
from typing import List, Dict, Any

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

import os
import re
from xml.sax.saxutils import escape


# --- Regex used by safe_text helpers (must be defined BEFORE functions that reference it) ---
_TAG_RE = re.compile(r"<[^>]+>")

# --- Logo configuration ---
LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "insight_hub_logo.png")


# --- Helpers: safe rendering + light markup we control ---


def safe_text(s: Any) -> str:
    """
    Make text safe for ReportLab Paragraph:
    - strip HTML tags like <a href=...>
    - replace problematic unicode spaces
    - escape &, <, >, quotes so ReportLab doesn't choke
    """
    if s is None:
        return ""
    s = str(s)
    s = _TAG_RE.sub("", s)          # remove HTML tags
    s = s.replace("\u00a0", " ")    # non-breaking spaces -> space
    s = escape(s)                   # escape &, <, >, quotes
    return s.strip()


def _plain_no_escape(s: Any) -> str:
    """
    Strip tags + normalize spaces, but do NOT escape.
    Use only when we will escape pieces ourselves.
    """
    if s is None:
        return ""
    s = str(s)
    s = _TAG_RE.sub("", s)
    s = s.replace("\u00a0", " ")
    return s.strip()


def _fmt_dt(dt: datetime | None) -> str:
    if not dt:
        return "Unknown"
    return dt.strftime("%Y-%m-%d %H:%M")


_VERB_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9\-\/]*)\b(.*)$")


def _bold_primary_verb(step: Any) -> str:
    """
    Turn: 'Review liquidity coverage...' into '<b>Review</b> liquidity coverage...'
    We keep markup minimal and only inject <b> around the first token.
    Everything else is escaped.
    """
    raw = _plain_no_escape(step)
    if not raw:
        return ""

    m = _VERB_RE.match(raw)
    if not m:
        return safe_text(raw)

    verb = escape(m.group(1))
    rest = escape(m.group(2) or "")
    return f"<b>{verb}</b>{rest}"


def _link_markup(url: str, display_text: str | None = None) -> str:
    """
    Return ReportLab-safe <link> markup.
    IMPORTANT: We escape display text, but keep the <link> tag (ReportLab paragraph markup).
    """
    u = (url or "").strip()
    if not u:
        return ""

    disp = display_text if (display_text is not None and display_text.strip()) else u
    return f'<link href="{escape(u)}" color="blue">{escape(disp)}</link>'


def render_action_cards(story, styles, cards: List[Dict], section_title: str):
    """
    Renders Action Cards.

    A+ rules:
    - The caller controls the section heading (no duplicated headers).
    - Render roles dynamically from the card (supports cyber/finance/healthcare).
    - Keep a deterministic role order so the report feels consistent.
    - If a role has no provided steps, show a fallback step (prevents visual gaps).
    - Improve scannability by bolding the primary action verb in each step.
    """
    if section_title:
        story.append(Paragraph(section_title, styles["IH_H2"]))

    preferred_role_orders = [
        ["IT Ops", "SecOps", "GRC/Legal"],  # Cyber
        ["Finance/Treasury", "Risk/Controls", "Compliance/Legal"],  # Finance
        ["Clinical Ops", "IT/SecOps", "Compliance/Legal"],  # Healthcare
    ]

    role_fallback = {
        "IT Ops": "Validate applicability against asset inventory and confirm remediation/mitigation posture where relevant.",
        "SecOps": "Increase monitoring for 24–72 hours for related indicators; escalate on confirmed exploitation or impact.",
        "GRC/Legal": "Confirm escalation path, documentation readiness, and any notification/disclosure triggers if impact is confirmed.",
        "Finance/Treasury": "Quantify exposure and sensitivity; validate liquidity/funding assumptions and near-term financial impact.",
        "Risk/Controls": "Validate control owners, monitoring signals, and escalation triggers; tune controls if loss/incident signals rise.",
        "Compliance/Legal": "Confirm regulatory perimeter, documentation readiness, and any reporting obligations if conditions escalate.",
        "Clinical Ops": "Validate operational exposure and define patient-impact triggers for clinical escalation if conditions worsen.",
        "IT/SecOps": "Confirm system owners, monitoring signals, backups/restore readiness (if relevant), and downtime runbooks.",
    }

    def choose_role_order(ns_keys: List[str]) -> List[str]:
        ns_set = set(ns_keys)
        for order in preferred_role_orders:
            if set(order).issubset(ns_set):
                extras = [k for k in ns_keys if k not in order]
                return order + extras

        if "Compliance/Legal" in ns_keys:
            others = [k for k in ns_keys if k != "Compliance/Legal"]
            return others + ["Compliance/Legal"]
        return ns_keys

    for c in cards:
        pr = c.get("priority")
        label = f"Priority {pr}" if pr else "Monitor"
        sev = safe_text(c.get("severity", ""))
        title = safe_text(c.get("title", ""))

        story.append(Paragraph(f"<b>{label} — {sev}: {title}</b>", styles["IH_Body"]))

        applies = c.get("applies_if", []) or []
        story.append(Paragraph(f"<b>Applies if:</b> {safe_text('; '.join(applies))}", styles["IH_Meta"]))

        story.append(Paragraph(f"<b>Implication:</b> {safe_text(c.get('implication', ''))}", styles["IH_Body"]))

        ns = c.get("next_steps", {}) or {}
        ns_keys = list(ns.keys())

        if not ns_keys:
            ns = {"Next step": ["Validate relevance and assign an owner for follow-up."]}
            ns_keys = ["Next step"]

        roles_in_order = choose_role_order(ns_keys)

        for role in roles_in_order:
            steps = ns.get(role, []) or []
            if not steps:
                steps = [role_fallback.get(role, "Validate relevance, assign an owner, and define an escalation trigger if risk increases.")]

            story.append(Paragraph(f"<b>Next steps — {safe_text(role)}:</b>", styles["IH_Meta"]))

            lf = ListFlowable(
                [ListItem(Paragraph(_bold_primary_verb(s), styles["IH_Body"])) for s in steps],
                bulletType="bullet",
                leftIndent=16
            )
            story.append(lf)

        story.append(Spacer(1, 8))


def render_appendix_items(story, styles, items: List[Dict]):
    """
    Full item details at the end to reduce 'jumbled' feel.
    Links are rendered as active hyperlinks (ReportLab <link> markup),
    not raw text that looks clickable but isn't.
    """
    story.append(Paragraph("Appendix: Full Item Details", styles["IH_H2"]))

    if not items:
        story.append(Paragraph("No high-signal items were selected for this window.", styles["IH_Body"]))
        return

    for idx, it in enumerate(items, start=1):
        title_txt = safe_text(it.get("title", ""))
        story.append(Paragraph(f"<b>{idx}. {title_txt}</b>", styles["IH_Body"]))

        src = safe_text(it.get("source", ""))
        link = (it.get("link") or "").strip()
        link_markup = _link_markup(link, "Open source article") if link else ""

        meta_lines = [
            f"<b>Severity:</b> {safe_text(it.get('severity', ''))} &nbsp;&nbsp; <b>Score:</b> {safe_text(it.get('score', ''))}",
            f"<b>Source:</b> {src} &nbsp;&nbsp; <b>Published:</b> {safe_text(_fmt_dt(it.get('published')))}",
        ]
        if link_markup:
            meta_lines.append(f"<b>Link:</b> {link_markup}")
        else:
            meta_lines.append(f"<b>Link:</b> {safe_text(it.get('link', ''))}")

        story.append(Paragraph("<br/>".join(meta_lines), styles["IH_Meta"]))

        summary = it.get("summary", "")
        if summary:
            s = str(summary)
            if len(s) > 600:
                s = s[:597] + "..."
            story.append(Paragraph(safe_text(s), styles["IH_Body"]))

        story.append(Spacer(1, 6))


def render_methodology_page(story, styles, brand: str):
    """
    Enterprise methodology page: explains how Daily Risk Level is computed and what the scores mean.
    Mirrors summarize.py.daily_risk_level() logic:
      - RED if any High severity OR avg(score of first 8) >= 80
      - YELLOW if any Medium severity OR avg(score of first 8) >= 55
      - else GREEN
    """
    story.append(PageBreak())
    story.append(Paragraph("Methodology: Severity & Risk Scoring", styles["IH_Title"]))

    story.append(Paragraph(
        "<b>Purpose:</b> The Severity Score is a directional decision aid designed to express operational and regulatory impact—not headline intensity.",
        styles["IH_Body"],
    ))

    story.append(Paragraph("<b>Inputs used:</b>", styles["IH_H2"]))
    inputs = [
        "Source credibility (e.g., regulators, tier-1 outlets, vendor advisories).",
        "Evidence strength (active exploitation/enforcement vs. commentary).",
        "Impact surface (regulated data, critical operations, systemic exposure).",
        "Time sensitivity (patch windows, deadlines, ongoing investigations).",
        "Industry applicability (bank/payments/fintech; hospital/payer/EHR; enterprise IT/security).",
    ]
    story.append(ListFlowable(
        [ListItem(Paragraph(safe_text(b), styles["IH_Body"])) for b in inputs],
        bulletType="bullet",
        leftIndent=16,
    ))

    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Daily Risk Level mapping (exact thresholds):</b>", styles["IH_H2"]))

    mapping = [
        "<b>RED (High):</b> Any item marked <b>High</b> severity <i>or</i> the average score (top 8 items) is <b>≥ 80</b>.",
        "<b>YELLOW (Moderate):</b> Any item marked <b>Medium</b> severity <i>or</i> the average score (top 8 items) is <b>≥ 55</b>.",
        "<b>GREEN (Low):</b> Otherwise (no High/Medium items and average score remains below thresholds).",
    ]
    story.append(ListFlowable(
        [ListItem(Paragraph(b, styles["IH_Body"])) for b in mapping],
        bulletType="bullet",
        leftIndent=16,
    ))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Interpretation guidance:</b> Scores are meant to improve consistency of prioritization across days. "
        "They do not represent a probabilistic forecast. Always validate applicability to your environment.",
        styles["IH_Body"],
    ))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        f"<b>About {safe_text(brand)}:</b> Daily, industry-specific intelligence designed to show what changed, why it matters, and what to watch next.",
        styles["IH_Meta"],
    ))


def _draw_logo(canvas, doc):
    """
    Draw a large, legible Insight Hub logo in the top-right header area on every page.
    """
    try:
        if not LOGO_PATH or not os.path.exists(LOGO_PATH):
            return

        canvas.saveState()

        page_w, page_h = doc.pagesize

        # Big enough to be legible
        logo_h = 0.95 * inch
        logo_w = 3.25 * inch

        # Push closer to the right edge (ignore text margin)
        x = page_w - logo_w - (0.25 * inch)
        y = page_h - doc.topMargin + 0.05 * inch

        canvas.drawImage(
            LOGO_PATH,
            x,
            y,
            width=logo_w,
            height=logo_h,
            preserveAspectRatio=True,
            anchor="ne",
            mask="auto",
        )

        canvas.restoreState()
    except Exception:
        return
    

def _draw_header_footer(canvas, doc):
    """
    Header: logo (top-right)
    Footer: page number (bottom-right)
    """
    try:
        canvas.saveState()
        page_w, page_h = doc.pagesize

        # ---------- HEADER: LOGO ----------
        if LOGO_PATH and os.path.exists(LOGO_PATH):
            logo_h = 0.95 * inch
            logo_w = 3.25 * inch

            x = page_w - logo_w - (0.25 * inch)  # ignore text margin
            y = page_h - doc.topMargin + 0.15 * inch

            canvas.drawImage(
                LOGO_PATH,
                x,
                y,
                width=logo_w,
                height=logo_h,
                preserveAspectRatio=True,
                anchor="ne",
                mask="auto",
            )

        # ---------- FOOTER: PAGE NUMBER ----------
        canvas.setFont("Helvetica", 9)  # change to Helvetica-Bold if you want
        page_num = canvas.getPageNumber()
        canvas.drawRightString(
            page_w - doc.rightMargin,     # align with text block
            0.55 * inch,                  # safe above bottom edge
            f"Page {page_num}"
        )

        canvas.restoreState()
    except Exception:
        return






def build_pdf(
    out_path: str,
    brand: str,
    title: str,
    date_label: str,
    window_label: str,
    audience: str,
    snapshot_bullets: List[str],
    items: List[Dict],
    implication_bullets,  # can be List[str] OR List[Dict] (action cards)
    watch_bullets: List[str],
    risk_level: str,
):
    styles = getSampleStyleSheet()

    if "IH_Title" not in styles:
        styles.add(ParagraphStyle(
            name="IH_Title",
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            spaceAfter=10,
        ))
    if "IH_H2" not in styles:
        styles.add(ParagraphStyle(
            name="IH_H2",
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=15,
            spaceBefore=10,
            spaceAfter=8,
        ))
    if "IH_Body" not in styles:
        styles.add(ParagraphStyle(
            name="IH_Body",
            fontName="Helvetica",
            fontSize=10.5,
            leading=14,
            spaceAfter=6,
        ))
    if "IH_Meta" not in styles:
        styles.add(ParagraphStyle(
            name="IH_Meta",
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
            spaceAfter=6,
            wordWrap="CJK",
        ))




    doc = SimpleDocTemplate(
        out_path,
        pagesize=(8.5 * inch, 11 * inch),
        rightMargin=0.85 * inch,
        leftMargin=0.85 * inch,
        topMargin=1.15 * inch,
        bottomMargin=0.75 * inch,
    )

    story = []

    # Header / meta
    story.append(Spacer(1, 8))

    story.append(Paragraph(safe_text(title), styles["IH_Title"]))

    header_meta = (
        f"<b>Date:</b> {safe_text(date_label)}<br/>"
        f"<b>Coverage Window:</b> {safe_text(window_label)}<br/>"
        f"<b>Daily Risk Level:</b> {safe_text(risk_level)}<br/>"
        f"<b>Audience:</b> {safe_text(audience)}"
    )
    story.append(Paragraph(header_meta, styles["IH_Meta"]))
    story.append(Spacer(1, 10))

    # Executive Snapshot
    story.append(Paragraph("Executive Judgment (60-second read)", styles["IH_H2"]))
    snapshot_list = ListFlowable(
        [ListItem(Paragraph(safe_text(b), styles["IH_Body"])) for b in (snapshot_bullets or [])],
        bulletType="bullet",
        leftIndent=16,
    )
    story.append(snapshot_list)
    story.append(Spacer(1, 10))

    # Implications / Action Cards (priorities first)
    if implication_bullets and isinstance(implication_bullets[0], dict):
        cards = implication_bullets

        priorities = [c for c in cards if c.get("priority")]
        monitor = [c for c in cards if not c.get("priority")]

        if priorities:
            render_action_cards(
                story,
                styles,
                priorities,
                section_title="Today’s Top Priorities (Decision Section)",
            )

        if monitor:
            render_action_cards(
                story,
                styles,
                monitor,
                section_title="Additional Developments (Monitor)",
            )

    else:
        story.append(Paragraph("Implications", styles["IH_H2"]))
        lf2 = ListFlowable(
            [ListItem(Paragraph(safe_text(b), styles["IH_Body"])) for b in (implication_bullets or [])],
            bulletType="bullet",
            leftIndent=16
        )
        story.append(lf2)

    # What to Watch Next
    story.append(Paragraph("What to Watch Next (Forward Signals)", styles["IH_H2"]))
    watch_list = ListFlowable(
        [ListItem(Paragraph(safe_text(b), styles["IH_Body"])) for b in (watch_bullets or [])],
        bulletType="bullet",
        leftIndent=16,
    )
    story.append(watch_list)

    # Appendix at end (reduces jumbled feel)
    render_appendix_items(story, styles, items)

    # Methodology page (enterprise credibility)
    render_methodology_page(story, styles, brand)


    doc.build(
        story,
        onFirstPage=_draw_header_footer,
        onLaterPages=_draw_header_footer,
    )
