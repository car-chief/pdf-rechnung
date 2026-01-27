#!/usr/bin/env python3
"""
Project management utility for pdf-rechnung system.
Manages data organization, imports, and maintenance.
"""

import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
XML_RAW_DIR = PROJECT_ROOT / "xml" / "raw"
XML_CLEANED_DIR = PROJECT_ROOT / "xml" / "cleaned"
BACKUP_DIR = DATA_DIR / "backups"


def cmd_structure(args):
    """Show project structure."""
    print("\n📁 PDF Rechnungen - Projektstruktur\n")
    print("├── app/")
    print("│   ├── parsing/          Datenextraktion (PDF, XML)")
    print("│   ├── storage/          JSON Persistierung")
    print("│   ├── templates/        HTML Templates")
    print("│   └── main.py           FastAPI Server")
    print("│")
    print("├── data/")
    print("│   ├── json/            Datenbank (invoices.json, line_items.json)")
    print("│   └── backups/         Daten-Backups")
    print("│")
    print("├── xml/")
    print("│   ├── raw/             Original XML-Exporte (groß)")
    print("│   └── cleaned/         Bereinigte XML-Dateien (klein)")
    print("│")
    print("├── scripts/")
    print("│   ├── utils/           Datenverarbeitung (clean_xml.py, import_xml_data.py)")
    print("│   └── debug/           Debug & Test-Dateien")
    print("│")
    print("├── tests/               Unit Tests")
    print("└── Rechnungen/          PDF-Archive (Jahr-basiert)")
    print()


def cmd_backup(args):
    """Create backup of current database."""
    json_dir = DATA_DIR / "json"
    if not json_dir.exists():
        logger.error(f"Data directory not found: {json_dir}")
        return 1
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_subdir = BACKUP_DIR / timestamp
    backup_subdir.mkdir(exist_ok=True)
    
    import shutil
    for json_file in json_dir.glob("*.json"):
        shutil.copy2(json_file, backup_subdir / json_file.name)
        logger.info(f"Backed up: {json_file.name}")
    
    logger.info(f"✓ Backup created: {backup_subdir}")
    return 0


def cmd_info(args):
    """Show project information."""
    import json
    
    json_dir = DATA_DIR / "json"
    invoices_file = json_dir / "invoices.json"
    line_items_file = json_dir / "line_items.json"
    
    print("\n📊 Datenbankübersicht\n")
    
    # Invoices
    if invoices_file.exists():
        with open(invoices_file) as f:
            invoices = json.load(f)
        print(f"Rechnungen:         {len(invoices)} Einträge")
        
        # Year/Month breakdown
        year_month_counts = {}
        for inv in invoices:
            year = inv.get('invoice_year')
            month = inv.get('invoice_month')
            if year and month:
                key = f"{year}-{month:02d}"
                year_month_counts[key] = year_month_counts.get(key, 0) + 1
        
        if year_month_counts:
            print("\n  Nach Monat:")
            for key in sorted(year_month_counts.keys()):
                print(f"    {key}: {year_month_counts[key]} Rechnungen")
    else:
        print("Rechnungen:         (keine Daten)")
    
    # Line Items
    if line_items_file.exists():
        with open(line_items_file) as f:
            line_items = json.load(f)
        print(f"\nRechnungspositionen: {len(line_items)} Einträge")
    else:
        print("\nRechnungspositionen: (keine Daten)")
    
    # XML Files
    print(f"\nXML-Dateien:")
    if XML_RAW_DIR.exists():
        raw_files = list(XML_RAW_DIR.glob("*.xml"))
        print(f"  Raw:     {len(raw_files)} Dateien")
        for f in raw_files:
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"    - {f.name} ({size_mb:.1f} MB)")
    
    if XML_CLEANED_DIR.exists():
        cleaned_files = list(XML_CLEANED_DIR.glob("*.xml"))
        print(f"  Cleaned: {len(cleaned_files)} Dateien")
        for f in cleaned_files:
            size_kb = f.stat().st_size / 1024
            print(f"    - {f.name} ({size_kb:.0f} KB)")
    print()


def cmd_init(args):
    """Initialize project directories."""
    dirs = [
        DATA_DIR / "json",
        DATA_DIR / "backups",
        XML_RAW_DIR,
        XML_CLEANED_DIR,
        PROJECT_ROOT / "scripts" / "debug",
        PROJECT_ROOT / "scripts" / "utils",
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ {dir_path.relative_to(PROJECT_ROOT)}")
    
    logger.info("✓ Project directories initialized")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='PDF Rechnungen - Projektmanagement',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python -m scripts.manage structure    # Projektstruktur anzeigen
  python -m scripts.manage info         # Datenbankstatus
  python -m scripts.manage backup       # Backup erstellen
  python -m scripts.manage init         # Verzeichnisse initialisieren
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Befehle')
    subparsers.add_parser('structure', help='Projektstruktur anzeigen')
    subparsers.add_parser('backup', help='Datenbank-Backup erstellen')
    subparsers.add_parser('info', help='Datenbankstatus anzeigen')
    subparsers.add_parser('init', help='Verzeichnisse initialisieren')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    commands = {
        'structure': cmd_structure,
        'backup': cmd_backup,
        'info': cmd_info,
        'init': cmd_init,
    }
    
    try:
        return commands[args.command](args) or 0
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
