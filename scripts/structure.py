#!/usr/bin/env python3
"""
Directory structure information and navigation script.

This project is organized into logical sections:
- app/: FastAPI application code
- data/: Persistent storage (JSON database)
- xml/: Data sources (raw and cleaned)
- scripts/: Utilities and debugging tools
- tests/: Unit and integration tests
"""

import os
from pathlib import Path

def show_structure():
    """Display project structure."""
    repo_root = Path(__file__).parent
    
    structure = {
        "app": "FastAPI application",
        "data": "Persistent storage (JSON, backups)",
        "xml": "Data sources (raw imports, cleaned versions)",
        "scripts": "Utilities and debugging",
        "tests": "Unit tests",
        "Rechnungen": "PDF archives",
    }
    
    print("📁 Project Structure")
    print("=" * 50)
    for dir_name, description in structure.items():
        path = repo_root / dir_name
        if path.exists():
            print(f"✓ {dir_name:20} - {description}")
        else:
            print(f"✗ {dir_name:20} - {description} (missing)")
    
    print("\n📚 Data Locations")
    print("=" * 50)
    print(f"JSON Database:     data/json/")
    print(f"XML Raw:           xml/raw/")
    print(f"XML Cleaned:       xml/cleaned/")
    print(f"Utility Scripts:   scripts/utils/")
    print(f"Debug Scripts:     scripts/debug/")
    
    print("\n🚀 Quick Commands")
    print("=" * 50)
    print("Start server:      python -m uvicorn app.main:app --reload")
    print("Import XML:        python scripts/utils/import_xml_data.py")
    print("Clean XML:         python scripts/utils/clean_xml.py")
    print("Run tests:         python -m pytest tests/")

if __name__ == "__main__":
    show_structure()
