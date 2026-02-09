import os
import re
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# Configuration
OUTPUT_DIR = "output"
TEMPLATE_DIR = "insight-hub/insight_hub/templates"
LOGO_PATH = "insight-hub/logo.png"

def parse_filename(filename):
    # Expected: InsightHub_sector_name_YYYY-MM-DD.html
    # Regex to capture sector and date
    match = re.match(r"InsightHub_(.+)_(\d{4}-\d{2}-\d{2})\.html", filename)
    if match:
        raw_sector_key = match.group(1).replace("_", " ").title()
        
        # Mapping for display names
        sector_map = {
            "Newsletter": "AI"
        }
        raw_sector = sector_map.get(raw_sector_key, raw_sector_key)
        
        date_str = match.group(2)
        # Convert date to nicer format
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        nice_date = dt.strftime("%B %d, %Y")
        return {
            "sector": raw_sector,
            "date_obj": dt,
            "date_str": nice_date,
            "filename": filename
        }
    return None

def generate_site():
    print("--- Genering Static Site Index ---")
    
    # 1. Scan Output Directory
    if not os.path.exists(OUTPUT_DIR):
        print(f"Error: {OUTPUT_DIR} does not exist. Run run.py first.")
        return

    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".html") and f != "index.html"]
    
    # 2. Group by Sector
    sectors = {}
    for f in files:
        data = parse_filename(f)
        if data:
            sec = data["sector"]
            if sec not in sectors:
                sectors[sec] = []
            sectors[sec].append(data)

    # 3. Sort Reports by Date (Newest First)
    for sec in sectors:
        sectors[sec].sort(key=lambda x: x["date_obj"], reverse=True)

    # 4. Sort Sectors Alphabetically
    sorted_sectors = dict(sorted(sectors.items()))

    # 4.5 Aggregate all reports for JSON
    all_reports = []
    for sector_reports in sectors.values():
        all_reports.extend(sector_reports)
    
    # Sort all reports by date
    all_reports.sort(key=lambda x: x["date_obj"], reverse=True)

    # JSON Serializer for datetime
    import json
    def json_serial(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError (f"Type {type(obj)} not serializable")

    all_reports_json = json.dumps(all_reports, default=json_serial)

    # 5. Load Logo
    logo_src = ""
    if os.path.exists(LOGO_PATH):
        import base64
        with open(LOGO_PATH, "rb") as img_f:
            b64_str = base64.b64encode(img_f.read()).decode("utf-8")
            logo_src = f"data:image/png;base64,{b64_str}"

    # 6. Render Index
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("index.html")
    
    html_out = template.render(
        sectors=sorted_sectors,
        all_reports_json=all_reports_json,
        logo_src=logo_src
    )

    index_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(index_path, "w") as f:
        f.write(html_out)

    print(f"Site Index generated at: {index_path}")

    # 7. Render Settings Page
    settings_template = env.get_template("settings.html")
    settings_html = settings_template.render(
        logo_src=logo_src
    )
    
    settings_path = os.path.join(OUTPUT_DIR, "settings.html")
    with open(settings_path, "w") as f:
        f.write(settings_html)
    print(f"Settings page generated at: {settings_path}")
    print("You can now upload the 'output' folder to any static host (Netlify, GitHub Pages).")

if __name__ == "__main__":
    generate_site()
