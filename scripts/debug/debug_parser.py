#!/usr/bin/env python3
"""
Quick debugging script to test PDF parsing.
"""
import traceback
from pathlib import Path
from app.parsing.extract import parse_invoice

# Test with one of the failing PDFs
test_file = Path("Rechnungen/2025/documents - 2025-01-06T102331.808.pdf")
abs_path = Path("Rechnungen") / "2025" / "documents - 2025-01-06T102331.808.pdf"

# Find actual file
import glob
pdfs = glob.glob("Rechnungen/**/*.pdf", recursive=True)
if pdfs:
    test_file = pdfs[1]  # Test second PDF (first one was parsed OK)
    print(f"Testing: {test_file}")
    
    try:
        invoice, error = parse_invoice(Path(test_file), test_file)
        if error:
            print(f"Error: {error}")
        else:
            print(f"Success! Invoice ID: {invoice.id}")
            print(f"  Vendor: {invoice.vendor}")
            print(f"  Invoice #: {invoice.invoice_number}")
            print(f"  Date: {invoice.invoice_date}")
            print(f"  Gross Total: {invoice.gross_total}")
    except Exception as e:
        print(f"Exception: {e}")
        traceback.print_exc()
else:
    print("No PDFs found")
