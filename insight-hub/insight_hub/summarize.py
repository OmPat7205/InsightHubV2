from typing import List, Dict, Any
import re


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def _detect_themes(items: List[Dict], industry_key: str) -> dict:
    theme_map = {
        "cybersecurity": {
            "active_exploit": ["actively exploited", "in the wild", "zero-day", "0-day"],
            "vuln_patch": ["cve", "vulnerability", "patch", "critical", "remote code execution", "rce"],
            "breach": ["breach", "data leak", "exfiltration", "stolen data", "data theft", "unauthorized access"],
            "ransomware": ["ransomware", "double extortion", "extortion", "leak site"],
            "regulatory": ["sec", "ftc", "doj", "compliance", "enforcement", "disclosure", "gdpr", "cnil", "fine"],
        },
        "healthcare": {
            "regulatory": ["cms", "hhs", "oig", "hipaa", "compliance", "audit", "enforcement"],
            "labor": ["strike", "nurse", "staffing", "union", "overtime", "shortage"],
            "ops_disruption": ["downtime", "outage", "disruption", "delayed care", "elective procedures"],
            "cost_pressure": ["cost", "margin", "reimbursement", "rate", "payment"],
            "vendor_risk": ["vendor", "third-party", "ehr", "claims", "billing"],
        },
        "financial_services": {
            "regulatory": ["sec", "fed", "occ", "cfpb", "enforcement", "guidance", "rule"],
            "liquidity_capital": ["liquidity", "capital", "stress test", "funding", "deposit"],
            "fraud": ["fraud", "scam", "money laundering", "aml"],
            "market_structure": ["payment", "fintech", "settlement", "clearing"],
            "systemic": ["systemic", "contagion", "bank run"],
        },
    }

    keys = theme_map.get(industry_key, {})
    counts = {k: 0 for k in keys.keys()}
    drivers = {k: [] for k in keys.keys()}

    for it in items:
        text = _norm((it.get("title", "") or "") + " " + (it.get("summary", "") or ""))
        for theme, markers in keys.items():
            if any(m in text for m in markers):
                counts[theme] += 1
                if len(drivers[theme]) < 2:
                    drivers[theme].append((it.get("title", "") or "")[:120])

    return {"counts": counts, "drivers": drivers}


def _risk_landscape_sentence(items: List[Dict], industry_key: str) -> str:
    if not items:
        return "No high-signal developments detected in the coverage window."

    high = [i for i in items if i.get("severity") == "High"]
    med = [i for i in items if i.get("severity") == "Medium"]

    themes = _detect_themes(items, industry_key).get("counts", {})
    top_theme = max(themes, key=lambda k: themes[k]) if themes else None

    if industry_key == "cybersecurity":
        blob = " ".join(
            _norm((it.get("title") or "") + " " + (it.get("summary") or "")) for it in items[:8]
        )

        has_active = any(k in blob for k in ["actively exploited", "in the wild", "zero-day", "0-day"])
        has_poc = any(k in blob for k in ["exploit code", "proof-of-concept", "poc", "weaponized"])
        has_patch = any(k in blob for k in ["patch tuesday", "patches", "security holes", "cve", "vulnerability"])
        has_incident = any(k in blob for k in ["breach", "ransomware", "exfiltration", "data leak", "data theft"])

        if high or has_active:
            return "Today reflects an incident-focused risk environment, with near-term compromise risk requiring rapid mitigation on the top items."
        if (med or has_incident) and (has_patch or has_poc):
            return "Today reflects a mitigation-focused risk environment, driven by patch adoption pressure and exposure risk from newly public exploit information."
        if med:
            return "Today reflects a moderate risk environment, with targeted items requiring validation and prioritized remediation where exposure exists."
        return "Today reflects a low-to-moderate risk environment, with monitoring recommended rather than urgent action."

    if high:
        return "Today’s brief is driven by high-severity developments, with immediate attention required on the top-ranked items."
    if med and top_theme:
        return f"Today’s brief shows a moderate risk posture, led by {top_theme.replace('_', ' ')} developments."
    return "Today’s brief is dominated by low-to-moderate developments, with monitoring recommended rather than urgent action."


def executive_ai_snapshot(items: List[Dict], industry_key: str) -> List[str]:
    bullets: List[str] = []
    bullets.append(_risk_landscape_sentence(items, industry_key))

    if not items:
        bullets.append("Action: Continue monitoring; no urgent operational changes recommended.")
        return bullets

    top = items[:3]

    if industry_key == "cybersecurity":
        for it in top:
            sev = it.get("severity", "Low")
            title = (it.get("title") or "").strip()
            text = _norm(title + " " + (it.get("summary") or ""))

            if len(title) > 140:
                title = title[:137] + "..."

            if any(k in text for k in ["cnil", "fine", "penalty", "sanction", "consent decree", "enforcement action"]):
                label = f"{sev}: {title} (regulatory enforcement signal)"
            elif any(k in text for k in ["exploit code", "proof-of-concept", "poc", "weaponized"]):
                label = f"{sev}: {title} (exposure risk: public exploit availability)"
            elif any(k in text for k in ["patch tuesday", "patches", "security holes", "cve", "vulnerability", "rce", "remote code execution"]):
                label = f"{sev}: {title} (operational pressure: patch/adoption risk)"
            elif any(k in text for k in ["actively exploited", "in the wild", "zero-day", "0-day"]):
                label = f"{sev}: {title} (active exploitation indicators)"
            elif any(k in text for k in ["ransomware", "double extortion", "extortion", "data theft", "breach", "exfiltration", "data leak"]):
                label = f"{sev}: {title} (incident activity / downstream fraud risk)"
            else:
                label = f"{sev}: {title} (validate applicability)"

            bullets.append(label)

        bullets.append(
            "Action: Validate asset exposure, prioritize patching of externally reachable systems, and confirm incident escalation/documentation readiness."
        )
        return bullets

    if industry_key == "financial_services":
        for it in top:
            sev = it.get("severity", "Low")
            title = (it.get("title") or "").strip()
            text = _norm(title + " " + (it.get("summary") or ""))

            if len(title) > 140:
                title = title[:137] + "..."

            if any(k in text for k in ["enforcement", "consent order", "consent decree", "penalty", "fine", "sanction", "charged", "lawsuit"]):
                label = f"{sev}: {title} (regulatory enforcement)"
            elif any(k in text for k in ["guidance", "rule", "rulemaking", "final rule", "proposal", "deadline", "supervisory"]):
                label = f"{sev}: {title} (regulatory change / guidance)"
            elif any(k in text for k in ["liquidity", "funding", "deposit", "deposits", "bank run", "capital", "stress test", "basel", "cet1", "tier 1"]):
                label = f"{sev}: {title} (liquidity/capital stress signal)"
            elif any(k in text for k in ["fraud", "scam", "phishing", "synthetic identity", "aml", "money laundering", "kyc", "chargeback"]):
                label = f"{sev}: {title} (fraud/AML controls signal)"
            elif any(k in text for k in ["payment", "payments", "settlement", "clearing", "interchange", "processor", "ach", "fednow", "swift"]):
                label = f"{sev}: {title} (payments/market plumbing)"
            elif any(k in text for k in ["outage", "downtime", "disruption", "incident", "system failure"]):
                label = f"{sev}: {title} (operational resilience)"
            else:
                label = f"{sev}: {title} (validate exposure)"

            bullets.append(label)

        bullets.append(
            "Action: Quantify exposure (liquidity/capital, fraud losses, payments ops), align owners to near-term controls, and confirm regulatory/compliance readiness where applicable."
        )
        return bullets

    if industry_key == "healthcare":
        for it in top:
            sev = it.get("severity", "Low")
            title = (it.get("title") or "").strip()
            text = _norm(title + " " + (it.get("summary") or ""))

            if len(title) > 140:
                title = title[:137] + "..."

            if any(k in text for k in ["cms", "hhs", "oig", "ocr", "hipaa", "enforcement", "penalty", "fine", "settlement", "consent", "doj"]):
                label = f"{sev}: {title} (regulatory / compliance signal)"
            elif any(k in text for k in ["strike", "union", "nurse", "staffing", "overtime", "shortage"]):
                label = f"{sev}: {title} (labor / staffing continuity)"
            elif any(k in text for k in ["downtime", "outage", "disruption", "delayed care", "diversion", "elective procedures"]):
                label = f"{sev}: {title} (operations disruption / patient impact)"
            elif any(k in text for k in ["vendor", "third-party", "ehr", "epic", "cerner", "claims", "billing", "clearinghouse"]):
                label = f"{sev}: {title} (vendor / platform dependency)"
            elif any(k in text for k in ["ransomware", "breach", "exfiltration", "data leak", "stolen", "unauthorized access", "phishing", "malware"]):
                label = f"{sev}: {title} (cyber + patient/PHI exposure)"
            elif any(k in text for k in ["cost", "margin", "reimbursement", "rate", "payment", "medicare", "medicaid", "denial", "prior authorization"]):
                label = f"{sev}: {title} (cost / reimbursement pressure)"
            else:
                label = f"{sev}: {title} (validate operational exposure)"

            bullets.append(label)

        bullets.append(
            "Action: Validate operational impact (staffing, downtime, vendor dependency), confirm HIPAA/CMS compliance readiness, and prepare patient/PHI incident escalation if applicable."
        )
        return bullets

    for it in top:
        sev = it.get("severity", "Low")
        title = (it.get("title") or "").strip()
        if len(title) > 140:
            title = title[:137] + "..."
        bullets.append(f"{sev}: {title}")

    bullets.append("Action: Validate applicability to your institution and prioritize near-term control readiness where relevant.")
    return bullets


# --- Action cards functions remain as you provided (including the finance return fix). ---
# (Keeping them unchanged to avoid breaking your summarize.py <-> render_pdf.py contract.)

# NOTE: Your finance_action_cards() already includes the critical "return cards_sorted" fix.
# NOTE: The Methodology page is implemented in render_pdf.py to stay enterprise-safe and deterministic.

# (Paste your existing cyber_action_cards, finance_action_cards, healthcare_action_cards,
#  cyber_implications, implications, what_to_watch, daily_risk_level below unchanged.)

# ---------------------------
# KEEP YOUR EXISTING FUNCTIONS BELOW THIS LINE (unchanged)
# ---------------------------

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# PASTE THE REST OF YOUR PROVIDED FUNCTIONS HERE EXACTLY AS-IS:
# cyber_action_cards(...)
# finance_action_cards(...)
# healthcare_action_cards(...)
# cyber_implications(...)
# implications(...)
# what_to_watch(...)
# daily_risk_level(...)
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def executive_ai_snapshot(items: List[Dict], industry_key: str) -> List[str]:
    bullets: List[str] = []
    bullets.append(_risk_landscape_sentence(items, industry_key))

    if not items:
        bullets.append("Action: Continue monitoring; no urgent operational changes recommended.")
        return bullets

    top = items[:3]

    # --- Cyber (A+ labeling) ---
    if industry_key == "cybersecurity":
        for it in top:
            sev = it.get("severity", "Low")
            title = (it.get("title") or "").strip()
            text = _norm(title + " " + (it.get("summary") or ""))

            if len(title) > 140:
                title = title[:137] + "..."

            if any(k in text for k in ["cnil", "fine", "penalty", "sanction", "consent decree", "enforcement action"]):
                label = f"{sev}: {title} (regulatory enforcement signal)"
            elif any(k in text for k in ["exploit code", "proof-of-concept", "poc", "weaponized"]):
                label = f"{sev}: {title} (exposure risk: public exploit availability)"
            elif any(k in text for k in ["patch tuesday", "patches", "security holes", "cve", "vulnerability", "rce", "remote code execution"]):
                label = f"{sev}: {title} (operational pressure: patch/adoption risk)"
            elif any(k in text for k in ["actively exploited", "in the wild", "zero-day", "0-day"]):
                label = f"{sev}: {title} (active exploitation indicators)"
            elif any(k in text for k in ["ransomware", "double extortion", "extortion", "data theft", "breach", "exfiltration", "data leak"]):
                label = f"{sev}: {title} (incident activity / downstream fraud risk)"
            else:
                label = f"{sev}: {title} (validate applicability)"

            bullets.append(label)

        bullets.append(
            "Action: Validate asset exposure, prioritize patching of externally reachable systems, and confirm incident escalation/documentation readiness."
        )
        return bullets

    # --- Finance (A+ labeling) ---
    if industry_key == "financial_services":
        for it in top:
            sev = it.get("severity", "Low")
            title = (it.get("title") or "").strip()
            text = _norm(title + " " + (it.get("summary") or ""))

            if len(title) > 140:
                title = title[:137] + "..."

            if any(k in text for k in ["enforcement", "consent order", "consent decree", "penalty", "fine", "sanction", "charged", "lawsuit"]):
                label = f"{sev}: {title} (regulatory enforcement)"
            elif any(k in text for k in ["guidance", "rule", "rulemaking", "final rule", "proposal", "deadline", "supervisory"]):
                label = f"{sev}: {title} (regulatory change / guidance)"
            elif any(k in text for k in ["liquidity", "funding", "deposit", "deposits", "bank run", "capital", "stress test", "basel", "cet1", "tier 1"]):
                label = f"{sev}: {title} (liquidity/capital stress signal)"
            elif any(k in text for k in ["fraud", "scam", "phishing", "synthetic identity", "aml", "money laundering", "kyc", "chargeback"]):
                label = f"{sev}: {title} (fraud/AML controls signal)"
            elif any(k in text for k in ["payment", "payments", "settlement", "clearing", "interchange", "processor", "ach", "fednow", "swift"]):
                label = f"{sev}: {title} (payments/market plumbing)"
            elif any(k in text for k in ["outage", "downtime", "disruption", "incident", "system failure"]):
                label = f"{sev}: {title} (operational resilience)"
            else:
                label = f"{sev}: {title} (validate exposure)"

            bullets.append(label)

        bullets.append(
            "Action: Quantify exposure (liquidity/capital, fraud losses, payments ops), align owners to near-term controls, and confirm regulatory/compliance readiness where applicable."
        )
        return bullets

    # --- Healthcare (A+ labeling) ---
    if industry_key == "healthcare":
        for it in top:
            sev = it.get("severity", "Low")
            title = (it.get("title") or "").strip()
            text = _norm(title + " " + (it.get("summary") or ""))

            if len(title) > 140:
                title = title[:137] + "..."

            if any(k in text for k in ["cms", "hhs", "oig", "ocr", "hipaa", "enforcement", "penalty", "fine", "settlement", "consent", "doj"]):
                label = f"{sev}: {title} (regulatory / compliance signal)"
            elif any(k in text for k in ["strike", "union", "nurse", "staffing", "overtime", "shortage"]):
                label = f"{sev}: {title} (labor / staffing continuity)"
            elif any(k in text for k in ["downtime", "outage", "disruption", "delayed care", "diversion", "elective procedures"]):
                label = f"{sev}: {title} (operations disruption / patient impact)"
            elif any(k in text for k in ["vendor", "third-party", "ehr", "epic", "cerner", "claims", "billing", "clearinghouse"]):
                label = f"{sev}: {title} (vendor / platform dependency)"
            elif any(k in text for k in ["ransomware", "breach", "exfiltration", "data leak", "stolen", "unauthorized access", "phishing", "malware"]):
                label = f"{sev}: {title} (cyber + patient/PHI exposure)"
            elif any(k in text for k in ["cost", "margin", "reimbursement", "rate", "payment", "medicare", "medicaid", "denial", "prior authorization"]):
                label = f"{sev}: {title} (cost / reimbursement pressure)"
            else:
                label = f"{sev}: {title} (validate operational exposure)"

            bullets.append(label)

        bullets.append(
            "Action: Validate operational impact (staffing, downtime, vendor dependency), confirm HIPAA/CMS compliance readiness, and prepare patient/PHI incident escalation if applicable."
        )
        return bullets

    # --- Default ---
    for it in top:
        sev = it.get("severity", "Low")
        title = (it.get("title") or "").strip()
        if len(title) > 140:
            title = title[:137] + "..."
        bullets.append(f"{sev}: {title}")

    bullets.append("Action: Validate applicability to your institution and prioritize near-term control readiness where relevant.")
    return bullets


def cyber_action_cards(items: List[Dict]) -> List[Dict]:
    cards: List[Dict] = []

    enforcement_terms = [
        "fine", "penalty", "sanction", "consent decree", "consent order", "settlement",
        "enforcement action", "charged", "charges", "prosecution", "lawsuit", "order"
    ]
    regulator_terms = ["cnil", "sec", "ftc", "doj", "data protection authority", "regulator", "regulatory"]
    privacy_context_terms = ["gdpr", "hipaa", "disclosure", "notification", "reporting"]

    for it in items[:5]:
        title = (it.get("title") or "").strip()
        summary = (it.get("summary") or "").strip()
        text = _norm(title + " " + summary)
        sev = it.get("severity", "Low")

        applies: List[str] = []

        if any(k in text for k in ["microsoft", "windows", "m365", "office 365", "azure", "exchange", "patch tuesday"]):
            applies.append("Microsoft Windows / Microsoft cloud (M365/Azure/Exchange) environments")

        if any(k in text for k in ["fortinet", "fortisiem", "fortifone", "fortigate", "fortios"]):
            applies.append("Fortinet environments (FortiSIEM/FortiFone/FortiGate/FortiOS as applicable)")

        if "servicenow" in text:
            applies.append("ServiceNow instances, especially with AI/chatbot features and integrations")

        is_active_exploit = any(k in text for k in ["zero-day", "0-day", "actively exploited", "in the wild"])
        is_public_exploit = any(k in text for k in ["exploit code", "proof-of-concept", "poc", "weaponized", "exploit released", "public exploit"])
        is_patch_wave = any(k in text for k in ["patch tuesday", "112 cves", "113 security holes", "security holes", "patches"])
        is_vuln = any(k in text for k in ["cve", "vulnerability", "rce", "remote code execution", "command injection", "unauthenticated"])

        is_ransomware = any(k in text for k in ["ransomware", "double extortion", "extortion", "encrypt", "encryption", "leak site", "data theft"])
        is_breach = any(k in text for k in [
            "breach", "data breach", "exfiltration", "data leak", "leak",
            "stolen", "stole", "unauthorized access", "exposed", "compromised"
        ])

        has_regulator = any(k in text for k in regulator_terms)
        has_enforcement = has_regulator and any(k in text for k in enforcement_terms)
        has_privacy_context = any(k in text for k in privacy_context_terms) or ("gdpr" in text) or ("hipaa" in text)

        is_saas = any(k in text for k in ["servicenow", "saas", "chatbot", "api", "oauth", "token", "integration"])
        is_healthcare_context = any(k in text for k in ["healthcare", "hospital", "clinic", "patient", "hipaa"])
        is_travel_context = any(k in text for k in ["traveler", "reservation", "booking", "rail", "airline", "hotel"])
        is_linux_or_malware = any(k in text for k in ["linux", "malware", "botnet", "c2", "command-and-control", "command and control", "backdoor", "loader", "trojan", "implant", "voidlink"])

        if has_enforcement:
            applies.append("Organizations with regulatory exposure and prior incident history (enforcement/penalty precedent risk)")
        elif has_privacy_context and (is_breach or is_ransomware):
            applies.append("Organizations with breach notification obligations (GDPR/HIPAA and similar regimes) and customer-facing PII exposure")

        if is_ransomware:
            applies.append("Organizations with sensitive data exposure and weak backup segmentation or limited restoration testing")

        if any(k in text for k in ["zero-day", "0-day", "actively exploited", "in the wild", "unauthenticated", "remote"]):
            applies.append("Internet-facing or externally reachable deployments (highest urgency)")

        if not applies and (is_breach or is_ransomware):
            if is_healthcare_context:
                applies.append("Healthcare orgs handling patient/insurance data (HIPAA exposure) and customer-facing portals")
            elif is_travel_context:
                applies.append("Organizations with customer reservation/booking data and identity/PII exposure")
            else:
                applies.append("Organizations with customer-facing portals, identity/PII exposure, or third-party SaaS dependencies")

        if not applies:
            applies.append("Validate relevance against asset inventory and vendor list")

        if is_active_exploit:
            implication = "Active exploitation indicators shift risk to immediate: treat exposure reduction and mitigation as same-day priorities."
        elif is_public_exploit and (is_vuln or "command injection" in text):
            implication = "Public exploit availability increases opportunistic attack likelihood, especially for unpatched or externally reachable deployments."
        elif is_patch_wave:
            implication = "Patch volume increases the chance of missed remediation; attackers often pivot quickly once patch adoption lags."
        elif is_vuln:
            implication = "Practical risk hinges on deployment scope and exposure; prioritize remediation on internet-facing and high-privilege assets first."
        elif is_ransomware:
            implication = "Ransomware activity implies data theft and operational disruption; prioritize containment, restoration readiness, and extortion/fraud follow-on monitoring."
        elif has_enforcement:
            implication = "Regulatory enforcement sets precedent and raises expectations for defensible controls and documentation; ensure evidence capture and reporting readiness."
        elif is_breach:
            implication = "Breach disclosures elevate downstream fraud/phishing risk; strengthen customer-facing monitoring, communications readiness, and notification decisioning."
        else:
            implication = "Security-relevant development requiring applicability validation and monitoring for escalation signals."

        it_ops: List[str] = []
        sec_ops: List[str] = []
        grc: List[str] = []

        if has_enforcement:
            it_ops.append("Validate privacy/security control posture (access logging, auth hardening, retention, encryption) and ensure evidence capture exists for audits/inquiries.")
        else:
            it_ops.append("Confirm whether affected systems/features exist in the environment (asset + vendor inventory).")

        if is_active_exploit or is_public_exploit or is_vuln or is_patch_wave:
            it_ops.append("Validate patch/mitigation status on exposed/high-privilege assets first; restrict external exposure until verified.")
            sec_ops.append("Increase monitoring and triage for 24–72 hours around affected systems (auth anomalies, execution, lateral movement).")

        if is_patch_wave:
            it_ops.append("Prioritize remediation by exposure + criticality (internet-facing, domain controllers, email, identity).")
            sec_ops.append("Track patch adoption coverage; escalate if critical systems remain unpatched beyond the first remediation window.")

        if is_saas:
            it_ops.append("Review SaaS configuration and integration permissions (tokens, connected apps, least privilege).")
            sec_ops.append("Monitor SaaS audit logs for unusual access patterns, data access, or integration abuse.")
            grc.append("Validate vendor risk posture and confirm internal documentation for third-party reliance.")

        if is_linux_or_malware:
            sec_ops.append("Hunt for C2 beacons, suspicious outbound connections, and persistence mechanisms on Linux fleets; prioritize internet-facing hosts and servers.")
            it_ops.append("Confirm EDR/agent coverage on Linux systems and review egress controls/DNS logging for high-signal detection.")

        if is_ransomware:
            it_ops.append("Validate backup integrity and restoration path; ensure immutable/offline copies where available.")
            sec_ops.append("Hunt for lateral movement and persistence; validate containment boundaries and privileged access integrity.")
            grc.append("Prepare notification decisioning and comms posture; track leak-site or extortion developments.")

        if is_breach and not is_ransomware:
            if is_healthcare_context:
                sec_ops.append("Monitor for patient-portal phishing, call-center social engineering, and credential-stuffing attempts tied to the breach.")
            elif is_travel_context:
                sec_ops.append("Monitor for account takeover, refund/chargeback fraud patterns, and phishing using travel/booking data.")
            else:
                sec_ops.append("Monitor for phishing/scam follow-ons using breached data; coordinate comms and user advisories if needed.")

            grc.append("Confirm notification thresholds and maintain complete, time-stamped incident documentation for decision defensibility.")

        if has_privacy_context and not has_enforcement and (is_breach or is_ransomware):
            grc.append("Confirm notification obligations (GDPR/HIPAA and applicable regimes) and ensure defensible documentation for decision timelines.")

        if has_enforcement:
            grc.append("Confirm escalation timelines and reporting expectations align with the regulator’s enforcement posture and any applicable orders.")

        if not grc:
            grc.append("Confirm escalation path and documentation readiness if exploitation or confirmed impact is detected.")

        cards.append(
            {
                "title": title,
                "severity": sev,
                "applies_if": applies[:3],
                "implication": implication,
                "next_steps": {
                    "IT Ops": it_ops[:3],
                    "SecOps": sec_ops[:3],
                    "GRC/Legal": grc[:2],
                },
            }
        )

    severity_rank = {"High": 3, "Medium": 2, "Low": 1}

    def score_card(c: Dict) -> int:
        s = severity_rank.get(c.get("severity", "Low"), 0)
        t = _norm((c.get("title") or "") + " " + (c.get("implication") or ""))

        if any(k in t for k in ["actively exploited", "in the wild", "zero-day", "0-day"]):
            s += 3
        if any(k in t for k in ["exploit code", "proof-of-concept", "poc", "weaponized", "public exploit"]):
            s += 2
        if any(k in t for k in ["cve", "vulnerability", "rce", "remote code execution", "command injection", "unauthenticated"]):
            s += 1
        if any(k in t for k in ["patch tuesday", "patch volume", "security holes", "patch adoption"]):
            s += 1
        if "ransomware" in t or "extortion" in t:
            s += 1
        if any(k in t for k in ["breach", "data leak", "exfiltration", "stolen", "unauthorized access"]):
            s += 1
        if any(k in t for k in ["enforcement", "fine", "sanction", "penalty", "consent decree", "consent order", "settlement", "cnil", "sec", "ftc", "doj"]):
            s += 1

        return s

    cards_sorted = sorted(cards, key=score_card, reverse=True)
    for i, c in enumerate(cards_sorted):
        c["priority"] = i + 1 if i < 3 else None
    return cards_sorted


def finance_action_cards(items: List[Dict]) -> List[Dict]:
    """
    Finance item-specific action cards with:
    - Applies-if targeting (bank vs fintech vs payments vs broker-dealer)
    - Distinct implications (no repetition)
    - Next steps by function (Finance/Treasury, Risk/Controls, Compliance/Legal)
    - Priority scoring that elevates liquidity/systemic/enforcement over generic market commentary
    """
    cards: List[Dict] = []

    regulator_terms = ["sec", "fed", "federal reserve", "occ", "cfpb", "fdic", "doj", "finra", "cftc", "ecb", "boe"]
    enforcement_terms = ["enforcement", "settlement", "consent order", "consent decree", "penalty", "fine", "sanction", "charged", "lawsuit"]
    guidance_terms = ["guidance", "rule", "rulemaking", "proposal", "final rule", "deadline", "supervisory", "circular"]

    liquidity_terms = ["liquidity", "funding", "deposit", "deposits", "run", "bank run", "capital", "stress test", "basel", "cet1", "tier 1", "leverage ratio"]
    market_terms = ["volatility", "sell-off", "yields", "yield", "rates", "treasury", "bond", "equity", "spread", "credit spreads"]
    fraud_terms = ["fraud", "scam", "phishing", "social engineering", "synthetic identity", "chargeback", "aml", "money laundering", "kyc", "fincrime"]
    payments_terms = ["payment", "payments", "card", "cards", "interchange", "settlement", "clearing", "swift", "ach", "fednow", "instant payments"]
    fintech_terms = ["fintech", "neobank", "crypto", "stablecoin", "tokenization", "defi", "wallet"]
    outage_terms = ["outage", "downtime", "disruption", "incident", "system failure"]

    for it in items[:6]:
        title = (it.get("title") or "").strip()
        summary = (it.get("summary") or "").strip()
        text = _norm(title + " " + summary)
        sev = it.get("severity", "Low")

        has_regulator = any(k in text for k in regulator_terms)
        has_enforcement = has_regulator and any(k in text for k in enforcement_terms)
        has_guidance = has_regulator and any(k in text for k in guidance_terms)

        is_liquidity = any(k in text for k in liquidity_terms)
        is_fraud = any(k in text for k in fraud_terms)
        is_payments = any(k in text for k in payments_terms)
        is_fintech = any(k in text for k in fintech_terms)
        is_market = any(k in text for k in market_terms)
        is_ops = any(k in text for k in outage_terms)

        applies: List[str] = []

        if any(k in text for k in ["bank", "deposits", "fdic", "occ", "credit union"]):
            applies.append("Banks/credit unions with deposit funding and supervisory oversight (FDIC/OCC/Fed)")
        if any(k in text for k in ["broker", "broker-dealer", "securities", "finra", "exchange", "clearing"]):
            applies.append("Broker-dealers / market intermediaries (FINRA/SEC oversight)")
        if is_payments or any(k in text for k in ["processor", "merchant", "interchange", "acquirer", "issuer"]):
            applies.append("Payments processors, issuers/acquirers, and merchant platforms (settlement/chargeback exposure)")
        if is_fintech:
            applies.append("Fintechs (partner-bank reliance, compliance uplift, and liquidity sensitivity)")
        if is_liquidity:
            applies.append("Institutions sensitive to funding/deposit flows or capital requirements (liquidity/capital stress)")
        if is_fraud:
            applies.append("Organizations with high-volume consumer transactions or onboarding risk (fraud/AML/KYC exposure)")
        if is_ops:
            applies.append("Firms with time-critical transaction processing or customer access requirements (operational resilience exposure)")

        if not applies:
            applies.append("Validate relevance to your products, customer base, and regulatory perimeter")

        if has_enforcement:
            implication = "Regulatory enforcement raises the cost of weak controls and weak documentation; assume a higher bar for evidence, monitoring, and governance."
        elif has_guidance:
            implication = "Supervisory guidance/rule changes can force near-term control updates and resourcing; missed deadlines turn into exam findings and penalties."
        elif is_liquidity:
            implication = "Liquidity/capital signals can change risk appetite and pricing quickly; funding stress typically cascades via confidence and counterparty behavior."
        elif is_fraud:
            implication = "Fraud/AML signals imply elevated loss rates and regulatory scrutiny; rapid attacker adaptation can outpace static controls."
        elif is_payments:
            implication = "Payments/settlement changes can create immediate operational and revenue impacts (disputes, latency, reconciliation, interchange)."
        elif is_ops:
            implication = "Operational disruption risk can turn into customer harm and regulatory escalation; resilience posture and incident comms must be tight."
        elif is_market:
            implication = "Market structure/volatility signals can alter hedging, margin, and client behavior; watch second-order effects (spreads, funding costs, counterparty limits)."
        else:
            implication = "Material finance-sector development requiring applicability validation and monitoring for escalation signals."

        finance_ops: List[str] = []
        risk: List[str] = []
        compliance: List[str] = []

        if is_liquidity:
            finance_ops.append("Review liquidity coverage, deposit concentration, and contingent funding sources; stress-test outflow scenarios.")
            finance_ops.append("Re-check pricing and risk appetite assumptions if funding costs or spreads are moving.")
        elif is_market:
            finance_ops.append("Validate hedging/margin assumptions and identify exposures sensitive to rate/spread moves.")
        elif is_payments:
            finance_ops.append("Assess revenue exposure (fees/interchange) and reconciliation/settlement timing impacts.")
        else:
            finance_ops.append("Validate business exposure and quantify near-term financial impact if the trend escalates.")

        if is_fraud:
            risk.append("Increase monitoring for account takeover, synthetic identity, and scam patterns; tighten onboarding and transaction controls where justified.")
        if is_ops:
            risk.append("Validate operational resilience controls (RTO/RPO, failover, incident runbooks) for critical payment/customer systems.")
        if is_liquidity:
            risk.append("Reassess counterparty and concentration limits under stress; monitor early-warning indicators (deposit flows, collateral, utilization).")
        if not risk:
            risk.append("Confirm control owners, monitoring signals, and escalation triggers if the risk profile changes.")

        if has_enforcement:
            compliance.append("Preserve evidence and documentation; align remediation and governance narratives to withstand regulatory scrutiny.")
        if has_guidance:
            compliance.append("Map requirements to owners and deadlines; identify control gaps and resource needs before the next exam cycle.")
        if is_fraud and ("aml" in text or "money laundering" in text or "kyc" in text):
            compliance.append("Validate AML/KYC policy alignment and documentation; ensure SAR/monitoring workflows are defensible.")
        if not compliance:
            compliance.append("Confirm regulatory perimeter and reporting obligations if conditions escalate.")

        cards.append({
            "title": title,
            "severity": sev,
            "applies_if": applies[:3],
            "implication": implication,
            "next_steps": {
                "Finance/Treasury": finance_ops[:3],
                "Risk/Controls": risk[:3],
                "Compliance/Legal": compliance[:2],
            },
        })

    # ✅ FIX: scoring + sort + priority + return
    severity_rank = {"High": 3, "Medium": 2, "Low": 1}

    def score_card(c: Dict) -> int:
        s = severity_rank.get(c.get("severity", "Low"), 0)
        t = _norm((c.get("title") or "") + " " + (c.get("implication") or ""))

        if any(k in t for k in ["enforcement", "settlement", "consent order", "consent decree", "penalty", "fine", "sanction", "charged", "lawsuit"]):
            s += 3
        if any(k in t for k in ["liquidity", "funding", "deposit", "bank run", "capital", "stress test", "basel", "cet1", "tier 1"]):
            s += 3
        if any(k in t for k in ["aml", "money laundering", "kyc", "fraud", "synthetic identity", "scam", "phishing"]):
            s += 2
        if any(k in t for k in ["payments", "settlement", "clearing", "interchange", "chargeback", "ach", "fednow"]):
            s += 1
        if any(k in t for k in ["outage", "downtime", "disruption", "operational resilience", "system failure"]):
            s += 1
        if any(k in t for k in ["guidance", "rule", "rulemaking", "final rule", "proposal", "deadline", "supervisory"]):
            s += 1

        return s

    cards_sorted = sorted(cards, key=score_card, reverse=True)
    for i, c in enumerate(cards_sorted):
        c["priority"] = i + 1 if i < 3 else None
    return cards_sorted


def healthcare_action_cards(items: List[Dict]) -> List[Dict]:
    """
    Healthcare item-specific action cards with:
    - Applies-if targeting (hospital/clinic, payers, EHR dependency, patient data exposure)
    - Distinct implications (no repetitive boilerplate)
    - Next steps by function:
        * Clinical Ops
        * IT/SecOps
        * Compliance/Legal
    - Priority scoring elevating patient-impact + regulatory enforcement + cyber disruption
    """
    cards: List[Dict] = []

    regulator_terms = ["cms", "hhs", "oig", "ocr", "hipaa", "doj", "state attorney general", "attorney general"]
    enforcement_terms = ["enforcement", "penalty", "fine", "settlement", "consent", "lawsuit", "charged", "order"]
    guidance_terms = ["guidance", "rule", "final rule", "proposal", "deadline", "audit", "inspection"]

    labor_terms = ["strike", "union", "nurse", "staffing", "overtime", "shortage", "walkout"]
    ops_terms = ["downtime", "outage", "disruption", "delayed care", "diversion", "elective procedures", "clinic closure"]
    vendor_terms = ["vendor", "third-party", "ehr", "epic", "cerner", "claims", "billing", "clearinghouse"]
    cyber_terms = ["ransomware", "breach", "exfiltration", "data leak", "stolen", "unauthorized access", "phishing", "malware"]
    cost_terms = ["cost", "margin", "reimbursement", "rate", "payment", "medicare", "medicaid", "denial", "prior authorization"]

    for it in items[:6]:
        title = (it.get("title") or "").strip()
        summary = (it.get("summary") or "").strip()
        text = _norm(title + " " + summary)
        sev = it.get("severity", "Low")

        has_regulator = any(k in text for k in regulator_terms)
        has_enforcement = has_regulator and any(k in text for k in enforcement_terms)
        has_guidance = has_regulator and any(k in text for k in guidance_terms)

        is_labor = any(k in text for k in labor_terms)
        is_ops = any(k in text for k in ops_terms)
        is_vendor = any(k in text for k in vendor_terms)
        is_cyber = any(k in text for k in cyber_terms)
        is_cost = any(k in text for k in cost_terms)

        applies: List[str] = []
        if any(k in text for k in ["hospital", "health system", "er", "ed", "emergency", "clinic"]):
            applies.append("Hospitals/health systems with patient-facing operations (ED/OR scheduling and continuity risk)")
        if any(k in text for k in ["payer", "insurer", "claims", "billing", "clearinghouse"]):
            applies.append("Providers/payers dependent on claims and revenue-cycle workflows (billing/denials/cashflow exposure)")
        if any(k in text for k in ["ehr", "epic", "cerner"]):
            applies.append("Organizations dependent on EHR uptime and integrations (clinical workflow + downtime procedures)")
        if is_cyber or "hipaa" in text:
            applies.append("Organizations handling PHI/PII with HIPAA obligations (patient notification + regulatory scrutiny)")
        if is_labor:
            applies.append("Facilities with staffing constraints or labor action risk (coverage, overtime, service prioritization)")
        if not applies:
            applies.append("Validate relevance to service lines, vendors, and compliance perimeter")

        if has_enforcement:
            implication = "Regulatory enforcement increases exposure for weak safeguards and weak documentation; assume higher scrutiny on HIPAA/security practices and timelines."
        elif has_guidance:
            implication = "Regulatory guidance/audit trends can force near-term policy and training updates; delayed remediation becomes exam findings and potential penalties."
        elif is_ops and is_vendor:
            implication = "Vendor-linked downtime can cascade into clinical disruption and patient harm; downtime procedures and communications become operationally critical."
        elif is_ops:
            implication = "Operational disruption risk can turn into delayed care and patient safety exposure; service prioritization and downtime playbooks must be ready."
        elif is_labor:
            implication = "Staffing shocks create continuity risk and quality-of-care pressure; mitigation requires scheduling, cross-coverage, and service triage decisions."
        elif is_cyber:
            implication = "Cyber/PHI exposure elevates patient notification and identity protection risk; treat containment and documentation as time-sensitive."
        elif is_cost:
            implication = "Reimbursement/cost pressure can force near-term service-line and staffing decisions; watch for margin compression and denials impacting cashflow."
        else:
            implication = "Material healthcare-sector development requiring applicability validation and monitoring for escalation signals."

        clinical_ops: List[str] = []
        it_secops: List[str] = []
        compliance_legal: List[str] = []

        if is_labor:
            clinical_ops.append("Assess coverage gaps (overtime, float pool, per-diem) and pre-plan service prioritization if staffing tightens.")
        if is_ops:
            clinical_ops.append("Validate downtime procedures (manual charting, med admin, scheduling) and confirm department-level readiness.")
        if not clinical_ops:
            clinical_ops.append("Validate operational exposure and define triggers for clinical escalation if conditions worsen.")

        if is_vendor:
            it_secops.append("Confirm vendor dependency map (EHR/claims/integrations) and validate failover/contingency access paths.")
        if is_cyber:
            it_secops.append("Increase monitoring for 24–72 hours (PHI access anomalies, lateral movement, credential abuse) and validate backups/restore paths.")
        if is_ops and not is_cyber:
            it_secops.append("Review incident runbooks (RTO/RPO, failover, comms) for systems tied to patient care and revenue cycle.")
        if not it_secops:
            it_secops.append("Confirm system owners, monitoring signals, and escalation triggers relevant to this development.")

        if has_enforcement:
            compliance_legal.append("Preserve evidence and ensure documentation is time-stamped and defensible; align remediation and governance narrative.")
        if is_cyber or "hipaa" in text:
            compliance_legal.append("Confirm HIPAA/privacy notification decisioning and documentation readiness (who/when/what thresholds).")
        if has_guidance:
            compliance_legal.append("Map requirements/audit themes to owners and deadlines; identify gaps and training needs before the next review cycle.")
        if not compliance_legal:
            compliance_legal.append("Confirm reporting obligations and internal escalation path if impact becomes patient-facing.")

        cards.append({
            "title": title,
            "severity": sev,
            "applies_if": applies[:3],
            "implication": implication,
            "next_steps": {
                "Clinical Ops": clinical_ops[:3],
                "IT/SecOps": it_secops[:3],
                "Compliance/Legal": compliance_legal[:2],
            },
        })

    severity_rank = {"High": 3, "Medium": 2, "Low": 1}

    def score_card(c: Dict) -> int:
        s = severity_rank.get(c.get("severity", "Low"), 0)
        t = _norm((c.get("title") or "") + " " + (c.get("implication") or ""))

        if any(k in t for k in ["enforcement", "penalty", "fine", "settlement", "consent", "oig", "ocr", "cms", "doj"]):
            s += 3
        if any(k in t for k in ["downtime", "outage", "disruption", "delayed care", "diversion"]):
            s += 3
        if any(k in t for k in ["ransomware", "breach", "exfiltration", "phishing", "malware"]):
            s += 2
        if any(k in t for k in ["strike", "staffing", "shortage", "overtime"]):
            s += 2
        if any(k in t for k in ["ehr", "epic", "cerner", "claims", "billing", "clearinghouse"]):
            s += 1
        if any(k in t for k in ["reimbursement", "margin", "denial", "payment", "medicare", "medicaid"]):
            s += 1

        return s

    cards_sorted = sorted(cards, key=score_card, reverse=True)
    for i, c in enumerate(cards_sorted):
        c["priority"] = i + 1 if i < 3 else None
    return cards_sorted


def cyber_implications(items: List[Dict]) -> List[str]:
    if not items:
        return [
            "No immediate cybersecurity implications identified within the coverage window. Maintain baseline monitoring and hygiene activities."
        ]

    text_blob = " ".join(_norm((it.get("title") or "") + " " + (it.get("summary") or "")) for it in items)
    implications: List[str] = []

    if any(k in text_blob for k in ["zero-day", "0-day", "actively exploited", "in the wild"]):
        implications.append("Where affected software is internet-facing or privileged, treat compromise risk as immediate and prioritize same-day mitigation and exposure reduction.")
    if any(k in text_blob for k in ["exploit code", "proof-of-concept", "poc", "weaponized"]):
        implications.append("Public exploit availability increases opportunistic attack likelihood; prioritize patching/mitigation on externally reachable assets before broad hardening.")
    if any(k in text_blob for k in ["cve", "vulnerability", "remote code execution", "rce", "patch"]):
        implications.append("Patch adoption gaps and incomplete asset inventories create silent exposure risk, especially in legacy, edge, and third-party-managed systems.")
    if any(k in text_blob for k in ["ransomware", "double extortion", "extortion"]):
        implications.append("Ransomware signals combined operational disruption and data theft risk; validate restoration readiness and monitor for extortion and fraud follow-ons.")
    if any(k in text_blob for k in ["breach", "data leak", "exfiltration", "stolen", "unauthorized access"]):
        implications.append("Breach disclosures elevate downstream fraud and phishing risk; tighten customer-facing monitoring and communications readiness.")
    if any(k in text_blob for k in ["fine", "sanction", "penalty", "enforcement action", "consent decree", "cnil", "sec", "ftc", "doj"]):
        implications.append("Regulatory enforcement increases the cost of delayed reporting or incomplete documentation; ensure defensible timelines and evidence capture.")

    if not implications:
        implications.append("Current developments increase monitoring requirements but do not yet force immediate operational decisions.")

    return implications[:4]


def implications(items: List[Dict], industry_key: str) -> List[Any]:
    # Cyber returns bullets (strings)
    if industry_key == "cybersecurity":
        return cyber_implications(items)

    # Healthcare returns action cards (dicts)
    if industry_key == "healthcare":
        return healthcare_action_cards(items)

    # Finance returns action cards (dicts)
    if industry_key == "financial_services":
        return finance_action_cards(items)

    if not items:
        return ["No immediate operational implications identified within the coverage window."]

    has_high = any(i.get("severity") == "High" for i in items)
    has_reg = any(
        any(k in _norm((i.get("title", "") + " " + (i.get("summary", "")))) for k in
            ["sec", "cms", "hhs", "cfpb", "occ", "enforcement", "regulation", "compliance"]
        )
        for i in items
    )

    out = []
    if has_high:
        out.append("Immediate exposure may exist for organizations with relevant systems/processes; prioritize validation and mitigation.")
    if has_reg:
        out.append("Compliance and reporting readiness should be reviewed; enforcement trends suggest tighter scrutiny.")
    out.append("Focus on the top-ranked items first; lower-ranked updates should be treated as background awareness unless conditions change.")
    return out[:4]


def what_to_watch(items: List[Dict], industry_key: str) -> List[str]:
    if not items:
        return ["Monitor for escalation from background activity to confirmed exploitation or operational impact."]

    text_blob = " ".join(_norm((it.get("title") or "") + " " + (it.get("summary") or "")) for it in items[:8])

    if industry_key == "cybersecurity":
        watch: List[str] = []
        has_fortinet = any(k in text_blob for k in ["fortinet", "fortisiem", "fortifone", "fortigate", "fortios"])
        has_poc = any(k in text_blob for k in ["exploit code", "proof-of-concept", "poc", "weaponized"])
        has_vuln = any(k in text_blob for k in ["cve", "vulnerability", "rce", "remote code execution", "command injection", "unauthenticated", "patch"])
        has_breach = any(k in text_blob for k in ["breach", "exfiltration", "data leak", "data theft", "stolen", "unauthorized access"])
        has_enforcement = any(k in text_blob for k in ["fine", "sanction", "penalty", "enforcement action", "consent decree", "cnil", "sec", "ftc", "doj"])
        has_linux_or_malware = any(k in text_blob for k in ["linux", "malware", "botnet", "c2", "command-and-control", "command and control", "backdoor", "loader", "trojan", "implant", "voidlink"])

        if has_poc or has_vuln:
            watch.append("Escalate if you see weaponized PoCs, exploit-kit integration, or mass scanning targeting newly disclosed vulnerabilities before patch adoption stabilizes.")
        if has_fortinet and (has_poc or has_vuln):
            watch.append("Track rapid attacker adoption against Fortinet products (internet scanning, exploitation attempts, or new intrusion clusters); this often precedes widespread compromise.")
        if has_breach:
            watch.append("Watch for follow-on phishing, fraud, or scam campaigns leveraging recently breached data; these can quickly turn into a business-impact event.")
        if has_enforcement:
            watch.append("Monitor for new enforcement actions or regulator commentary that materially changes disclosure expectations or documentation requirements.")
        if has_linux_or_malware:
            watch.append("Escalate if you see new C2 infrastructure, persistence modules, or cloud-token abuse tied to Linux malware activity; prioritize internet-facing servers and high-privilege hosts.")

        if not watch:
            watch.append("Monitor for any shift from vulnerability discussion to confirmed exploitation, operational disruption, or widespread attacker playbook adoption.")
        return watch[:5]

    if industry_key == "healthcare":
        watch: List[str] = []
        if any(k in text_blob for k in ["downtime", "outage", "disruption", "delayed care", "diversion"]):
            watch.append("Escalate if downtime spreads beyond a single facility/service line or triggers diversion/delayed care; that’s when operational risk becomes patient-safety risk.")
        if any(k in text_blob for k in ["ehr", "epic", "cerner", "claims", "billing", "clearinghouse", "vendor", "third-party"]):
            watch.append("Watch for vendor follow-on impacts (EHR or clearinghouse interruptions, claims backlogs) that shift risk into revenue-cycle and care continuity.")
        if any(k in text_blob for k in ["strike", "staffing", "shortage", "overtime", "union"]):
            watch.append("Escalate if staffing gaps extend into critical units (ED/ICU/OR) or overtime becomes unsustainable; service prioritization decisions follow quickly.")
        if any(k in text_blob for k in ["hipaa", "ocr", "oig", "cms", "enforcement", "penalty", "fine", "settlement"]):
            watch.append("Monitor for regulator commentary, audits, or enforcement actions that tighten documentation and notification expectations.")
        if any(k in text_blob for k in ["ransomware", "breach", "exfiltration", "phishing", "malware"]):
            watch.append("Escalate if attacker activity shifts from initial access to PHI access/exfiltration; notification and patient protection timelines become time-sensitive.")
        if not watch:
            watch.append("Monitor for patient-impact triggers, vendor disruptions, staffing escalations, or regulator actions that change next-day operational priorities.")
        return watch[:5]

    if industry_key == "financial_services":
        watch: List[str] = []
        if any(k in text_blob for k in ["liquidity", "funding", "deposit", "bank run", "capital", "stress test", "basel", "cet1"]):
            watch.append("Escalate if deposit outflows, funding spreads, or collateral calls accelerate; this is when liquidity stress becomes a confidence event.")
        if any(k in text_blob for k in ["enforcement", "fine", "sanction", "consent order", "consent decree", "sec", "occ", "cfpb", "fdic", "finra", "doj"]):
            watch.append("Monitor for follow-on enforcement, new exam priorities, or regulator statements that raise the compliance bar or change timelines.")
        if any(k in text_blob for k in ["fraud", "scam", "synthetic identity", "aml", "money laundering", "kyc", "chargeback"]):
            watch.append("Escalate if fraud rings adapt tactics (ATO spikes, synthetic IDs, mule activity) faster than control tuning; losses can step-change quickly.")
        if any(k in text_blob for k in ["payments", "settlement", "clearing", "interchange", "processor", "ach", "fednow"]):
            watch.append("Watch for settlement delays, reconciliation breaks, or dispute/chargeback surges—these turn operational issues into revenue and customer-harm events.")
        if not watch:
            watch.append("Monitor for regulator guidance, liquidity stress signals, or fraud pattern shifts that change next-day operational priorities.")
        return watch[:5]

    # ✅ Safe fallback
    return ["Monitor for follow-on guidance or operational changes that shift risk from background to execution."]


def daily_risk_level(items: List[Dict]) -> str:
    if not items:
        return "GREEN (Low)"

    severities = [i.get("severity", "Low") for i in items]
    scores = [float(i.get("score", 0) or 0) for i in items[:8]]
    avg_score = sum(scores) / max(len(scores), 1)

    if "High" in severities or avg_score >= 80:
        return "RED (High)"
    if "Medium" in severities or avg_score >= 55:
        return "YELLOW (Moderate)"
    return "GREEN (Low)"
