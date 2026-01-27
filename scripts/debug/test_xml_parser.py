#!/usr/bin/env python3
"""
Test the XML parser.
"""
from app.parsing.xml_parser import parse_invoices_from_xml

invoices = parse_invoices_from_xml("xml/2025-07-cleaned.xml")

print(f"Total invoices parsed: {len(invoices)}\n")

# Show first 5 invoices
for i, inv in enumerate(invoices[:5], 1):
    print(f"{i}. Invoice {inv.invoice_number}")
    print(f"   Date: {inv.invoice_date}")
    print(f"   Customer: {inv.vendor}")
    print(f"   Gross: {inv.gross_total}€")
    print(f"   Items: {len(inv.line_items)}")
    print()
