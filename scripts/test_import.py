#!/usr/bin/env python3
"""Test und Import der XML-Daten"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.storage import JSONStore

# Test JSONStore
store = JSONStore("data")
print(f"Store initialized: data/json/")

# Check files
invoices = store.load_invoices()
items = store.load_line_items()
print(f"  Invoices: {len(invoices)}")
print(f"  Line Items: {len(items)}")

# Now import XML data
from app.parsing.xml_parser import parse_invoices_from_xml

xml_file = Path("xml/cleaned/2025-07-cleaned.xml")
if not xml_file.exists():
    print(f"\nError: XML file not found: {xml_file}")
    print("Running cleanup first...")
    
    import subprocess
    result = subprocess.run(
        [sys.executable, "scripts/utils/clean_xml.py"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print("Error:", result.stderr)
        sys.exit(1)

# Parse invoices
print(f"\nParsing {xml_file}...")
invoices = parse_invoices_from_xml(str(xml_file), year=2025, month=7)
print(f"✓ Parsed {len(invoices)} invoices")

# Save to store
print("\nSaving to database...")
for inv in invoices:
    store.add_or_update_invoice(inv)

# Update line items
all_invoices = store.load_invoices()
all_line_items = []
for inv in all_invoices:
    all_line_items.extend(inv.line_items)

if all_line_items:
    store.save_line_items(all_line_items)

print(f"✓ Database updated")
print(f"  Total invoices: {len(store.load_invoices())}")
print(f"  Total line items: {len(store.load_line_items())}")
