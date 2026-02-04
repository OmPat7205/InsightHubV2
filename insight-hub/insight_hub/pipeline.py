import os
import datetime
from .sectors import SECTORS
from .ingest import fetch_rss_items
from .filter_rank import filter_and_rank, apply_quality_controls
from .window import now_et, compute_lookback_window, TIMEZONE
from .services.llm import analyze_sector
from .services.render import render_html, save_json, generate_filename, OUTPUT_DIR

def run_sector(sector_key: str):
    """
    Orchestrates the pipeline for a single sector.
    """
    sector = SECTORS.get(sector_key)
    if not sector:
        print(f"Error: Sector '{sector_key}' not found.")
        return

    print(f"--- Starting Pipeline for {sector.name} ---")

    # 1. Ingest
    print(f"Fetching RSS from {len(sector.rss_sources)} sources...")
    raw_items = fetch_rss_items(sector.rss_sources)
    print(f"Fetched {len(raw_items)} items.")

    # 2. Filter & Rank (Heuristic First Pass)
    now_dt = now_et(TIMEZONE)
    start, end = compute_lookback_window(now_dt)
    
    selected_items = filter_and_rank(
        raw_items,
        start=start,
        end=end,
        include_keywords=sector.include_keywords,
        exclude_keywords=sector.exclude_keywords
    )
    
    # De-duplicate
    selected_items = apply_quality_controls(selected_items, max_per_source=5)
    print(f"Selected {len(selected_items)} high-signal items for AI analysis.")

    # 3. AI Analysis (Gemini)
    print("Sending to Gemini for analysis...")
    analysis_result = analyze_sector(sector, selected_items)
    

    # Load and encode logo
    logo_path = os.path.join(os.path.dirname(__file__), "..", "logo.png")
    logo_src = ""
    if os.path.exists(logo_path):
        import base64
        with open(logo_path, "rb") as img_f:
            b64_str = base64.b64encode(img_f.read()).decode("utf-8")
            logo_src = f"data:image/png;base64,{b64_str}"

    # Sort Action Cards by Priority (High > Medium > Low)
    severity_order = {"High": 0, "Medium": 1, "Low": 2, "HIGH": 0, "MEDIUM": 1, "LOW": 2}
    
    if "action_cards" in analysis_result and isinstance(analysis_result["action_cards"], list):
        analysis_result["action_cards"].sort(
            key=lambda x: severity_order.get(x.get("severity", "Low"), 3)
        )

    # 4. Merge Data for Rendering
    report_data = {
        "title": sector.name,
        "date": now_dt.strftime("%B %d, %Y"),
        "generated_at": now_dt.isoformat(),
        "sector_name": sector.key.replace("_", " ").title(),
        "logo_src": logo_src,
        **analysis_result,  # Unloads executive_summary, risk_level, action_cards
        "sources": [{"title": item["title"], "link": item["link"], "source": item["source"]} for item in selected_items]
    }

    # 5. Render Output
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    base_name = generate_filename(sector.key)
    html_path = os.path.join(OUTPUT_DIR, f"{base_name}.html")
    json_path = os.path.join(OUTPUT_DIR, f"{base_name}.json")

    render_html(report_data, html_path)
    save_json(report_data, json_path)

    print(f"Done. Report ready at: {html_path}\n")

def run_all():
    """Runs pipeline for all configured sectors."""
    for key in SECTORS.keys():
        run_sector(key)
