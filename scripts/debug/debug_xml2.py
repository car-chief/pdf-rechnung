#!/usr/bin/env python3
"""
Debug XML parser with logging.
"""
import logging
logging.basicConfig(level=logging.DEBUG)

from app.parsing.xml_parser import parse_invoices_from_xml

invoices = parse_invoices_from_xml('xml/2025-07-cleaned.xml')
print(f'Total: {len(invoices)}')
if invoices:
    print(f'First invoice number: {invoices[0].invoice_number}')
