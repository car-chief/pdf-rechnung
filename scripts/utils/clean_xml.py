#!/usr/bin/env python3
"""
Clean up XML by removing unnecessary elements.
Usage: python clean_xml.py [input_file] [output_file]
"""
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

if len(sys.argv) >= 3:
    xml_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
else:
    # Default paths for xml/raw to xml/cleaned
    xml_path = Path("xml") / "raw" / "2025-07.xml"
    output_path = Path("xml") / "cleaned" / "2025-07-cleaned.xml"

print(f"Input:  {xml_path}")
print(f"Output: {output_path}")

if not xml_path.exists():
    print(f"Error: Input file not found: {xml_path}")
    sys.exit(1)

# Parse XML
tree = ET.parse(str(xml_path))
root = tree.getroot()

# Create new root
new_root = ET.Element("Orders")

# Copy Shop element as is
shop = root.find("Shop")
if shop is not None:
    new_root.append(shop)

# Process each Order
for order in root.findall("Order"):
    new_order = ET.Element("Order")
    
    # Keep only essential fields
    essential_fields = [
        "OrderNumber",
        "CustomerNumber", 
        "Currency",
        "GrandTotal",
        "TotalBeforeTax",
        "TotalTax",
        "CreationDate",
        "InvoicedOn",
    ]
    
    for field in essential_fields:
        elem = order.find(field)
        if elem is not None:
            new_field = ET.Element(field)
            new_field.text = elem.text
            new_order.append(new_field)
    
    # Add customer name from billing address
    billing_addr = order.find(".//BillingAddress")
    if billing_addr is not None:
        customer_name = ET.Element("CustomerName")
        first_name = billing_addr.find("FirstName")
        last_name = billing_addr.find("LastName")
        full_name = ""
        if first_name is not None and first_name.text:
            full_name += first_name.text
        if last_name is not None and last_name.text:
            if full_name:
                full_name += " "
            full_name += last_name.text
        customer_name.text = full_name
        new_order.append(customer_name)
    
    # Add invoice number
    invoice_num = order.find(".//InvoiceNumber")
    if invoice_num is not None:
        new_invoice = ET.Element("InvoiceNumber")
        new_invoice.text = invoice_num.text
        new_order.append(new_invoice)
    
    # Add line items (only actual products, skip shipping/payment)
    line_items_elem = ET.Element("LineItems")
    for line_item in order.findall(".//LineItem"):
        # Skip shipping and payment items
        item_id = line_item.find("Id")
        if item_id is None or item_id.text == "test":
            continue
        
        new_item = ET.Element("LineItem")
        
        # Keep: Id, Name, Quantity, UnitPrice, TotalPrice, TaxRate
        for field in ["Id", "Name", "Quantity", "UnitPrice", "TotalPrice", "TaxRate"]:
            elem = line_item.find(field)
            if elem is not None:
                new_field = ET.Element(field)
                new_field.text = elem.text
                new_item.append(new_field)
    
    new_root.append(new_order)

# Write cleaned XML
import os
os.makedirs(str(output_path.parent), exist_ok=True)
new_tree = ET.ElementTree(new_root)
ET.indent(new_tree, space="  ")  # Pretty print
with open(output_path, "wb") as f:
    new_tree.write(f, encoding="utf-8", xml_declaration=True)

print(f"✓ Cleaned XML saved to: {output_path}")
print(f"  Total orders: {len(new_root.findall('Order'))}")
orig_size = xml_path.stat().st_size / 1024
new_size = output_path.stat().st_size / 1024
reduction = (1 - new_size / orig_size) * 100 if orig_size > 0 else 0
print(f"  Size: {orig_size:.0f} KB → {new_size:.0f} KB ({reduction:.0f}% reduction)")

