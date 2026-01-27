#!/usr/bin/env python3
"""
Import invoices from XML into the database.
Supports importing from xml/cleaned/ directory.
"""
import logging
import sys
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.parsing.xml_parser import parse_invoices_from_xml
from app.storage import JSONStore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# XML source
xml_dir = Path("xml/cleaned")
if not xml_dir.exists():
    logger.error(f"XML directory not found: {xml_dir}")
    sys.exit(1)

# Import from XML
xml_files = sorted(xml_dir.glob("*.xml"))
if not xml_files:
    logger.error(f"No XML files found in {xml_dir}")
    sys.exit(1)

# Save to database
store = JSONStore("data")
total_invoices = 0
total_items = 0

for xml_file in xml_files:
    # Parse year and month from filename (e.g., "2025-07-cleaned.xml")
    parts = xml_file.stem.split("-")
    if len(parts) < 2:
        logger.warning(f"Skipping {xml_file.name} (invalid format)")
        continue
    
    try:
        year = int(parts[0])
        month = int(parts[1])
    except ValueError:
        logger.warning(f"Skipping {xml_file.name} (invalid year/month)")
        continue
    
    logger.info(f"Parsing {xml_file.name} (Year: {year}, Month: {month})")
    invoices = parse_invoices_from_xml(str(xml_file), year=year, month=month)
    logger.info(f"  Found {len(invoices)} invoices")
    
    # Save to database
    for invoice in invoices:
        store.add_or_update_invoice(invoice)
        logger.debug(f"  Saved: {invoice.invoice_number}")
    
    # Collect line items
    for invoice in invoices:
        total_items += len(invoice.line_items)
    
    total_invoices += len(invoices)

# Save line items
if total_items > 0:
    all_invoices = store.load_invoices()
    all_line_items = []
    for invoice in all_invoices:
        all_line_items.extend(invoice.line_items)
    store.save_line_items(all_line_items)
    logger.info(f"Saved {total_items} line items")

# Update index
index = store.load_index()
index.last_scanned = __import__('datetime').datetime.utcnow().isoformat()
store.save_index(index)

logger.info("=" * 50)
logger.info("✓ Import completed!")
logger.info(f"Total invoices in database: {len(store.load_invoices())}")
logger.info(f"Total line items: {len(store.load_line_items())}")
logger.info("=" * 50)
