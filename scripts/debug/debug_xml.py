#!/usr/bin/env python3
"""
Debug XML parser.
"""
import xml.etree.ElementTree as ET

tree = ET.parse("xml/2025-07-cleaned.xml")
root = tree.getroot()

print(f"Root tag: {root.tag}")
print(f"Total Orders: {len(root.findall('Order'))}")

# Check first order
order = root.find("Order")
if order is not None:
    print(f"\nFirst Order children:")
    for child in order:
        text = child.text[:50] if child.text else "(empty)"
        print(f"  {child.tag}: {text}")
    
    print(f"\nInvoiceNumber: {order.find('InvoiceNumber').text if order.find('InvoiceNumber') is not None else 'NOT FOUND'}")
else:
    print("No Order found!")
