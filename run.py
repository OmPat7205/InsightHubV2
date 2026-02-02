import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "insight-hub"))
from insight_hub.pipeline import run_all, run_sector

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific sector: python run.py cybersecurity
        run_sector(sys.argv[1])
    else:
        # Run all: python run.py
        run_all()
