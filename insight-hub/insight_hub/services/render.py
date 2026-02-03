import os
import json
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
OUTPUT_DIR = os.path.join(os.getcwd(), "output")

def render_html(data, output_path):
    """
    Renders the report using Jinja2 and saves as HTML.
    """
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("report.html")
    
    html_out = template.render(context=data)
    
    with open(output_path, "w") as f:
        f.write(html_out)
    
    print(f"HTML Report saved to: {output_path}")

def save_json(data, output_path):
    """
    Saves the raw intelligence data as JSON for web ingestion.
    """
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"JSON Data saved to: {output_path}")

def generate_filename(sector_key):
    """Generates timestamped filenames."""
    ts = datetime.now().strftime("%Y-%m-%d")
    return f"InsightHub_{sector_key}_{ts}"
