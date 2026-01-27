#!/usr/bin/env python3
"""
Debug script to find the exact error location.
"""
import traceback
import logging
from pathlib import Path
from app.parsing.extract import parse_invoice

logging.basicConfig(level=logging.DEBUG)

# Test with one of the failing PDFs
import glob
pdfs = glob.glob("Rechnungen/**/*.pdf", recursive=True)

if pdfs and len(pdfs) > 1:
    test_file = pdfs[1]  # Test second PDF (first one was parsed OK)
    print(f"Testing: {test_file}")
    
    try:
        invoice, error = parse_invoice(Path(test_file), test_file)
        if error:
            print(f"Error: {error}")
        else:
            print(f"Success! Invoice ID: {invoice.id}")
    except Exception as e:
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {e}")
        traceback.print_exc()
