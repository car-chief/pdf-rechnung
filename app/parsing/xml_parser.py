"""
XML-based invoice parsing instead of PDF parsing.
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import logging
import re
import hashlib

from .normalize import normalize_decimal, normalize_date
from ..storage.schema import Invoice, LineItem, ParsingStatus

logger = logging.getLogger(__name__)


def parse_invoices_from_xml(xml_path: str, year: int = 2025, month: Optional[int] = None) -> List[Invoice]:
    """
    Parse invoices directly from XML file.
    
    Args:
        xml_path: Path to XML file (e.g., "xml/2025-07-cleaned.xml")
        year: Invoice year for validation
        month: Month number (extracted from filename if None)
    
    Returns:
        List of Invoice objects
    """
    # Extract month from filename if not provided
    if month is None:
        import re
        match = re.search(r'2025-(\d{2})', xml_path)
        if match:
            month = int(match.group(1))
        else:
            month = 7  # Default fallback
    invoices = []
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        logger.error(f"Failed to parse XML {xml_path}: {e}")
        return []
    
    for order in root.findall("Order"):
        try:
            invoice = _parse_order_to_invoice(order, year, month)
            if invoice:
                invoices.append(invoice)
        except Exception as e:
            logger.error(f"Error parsing order: {e}", exc_info=True)
            continue
    
    logger.info(f"Parsed {len(invoices)} invoices from {xml_path}")
    return invoices


def _parse_order_to_invoice(order: ET.Element, year: int, month: int) -> Optional[Invoice]:
    """
    Convert an Order XML element to an Invoice object.
    """
    # Extract required fields
    invoice_number = _get_text(order, "InvoiceNumber")
    if not invoice_number:
        logger.debug("No invoice number found")
        return None
    
    # Create unique ID based on invoice number
    invoice_id = hashlib.sha256(f"{invoice_number}_{year}".encode()).hexdigest()
    
    # Extract dates
    invoiced_date = _get_text(order, "InvoicedOn")
    if invoiced_date:
        invoiced_date = invoiced_date.split("T")[0]  # Get YYYY-MM-DD part
    
    created_date = _get_text(order, "CreationDate")
    if created_date:
        created_date = created_date.split("T")[0]  # Get YYYY-MM-DD part
    
    # Create invoice
    invoice = Invoice(
        id=invoice_id,
        rel_path=f"xml/2025-{str(month).zfill(2)}-cleaned.xml",  # Placeholder path
        invoice_year=year,
        file_hash="",  # No file hash for XML source
    )
    
    invoice.invoice_number = invoice_number
    invoice.invoice_date = invoiced_date or created_date
    invoice.vendor = "Car-Chief.com"  # Fixed vendor from your data
    
    # Extract amounts
    gross_total = _get_text(order, "GrandTotal")
    net_total = _get_text(order, "TotalBeforeTax")
    tax_total = _get_text(order, "TotalTax")
    
    invoice.gross_total = normalize_decimal(gross_total) if gross_total else None
    invoice.net_total = normalize_decimal(net_total) if net_total else None
    invoice.vat_total = normalize_decimal(tax_total) if tax_total else None
    
    # Extract customer name
    customer_name = _get_text(order, "CustomerName")
    if customer_name:
        invoice.vendor = customer_name  # Use customer as the "vendor" for display
    
    # Extract line items
    line_items = []
    line_items_elem = order.find("LineItems")
    if line_items_elem is not None:
        for idx, item_elem in enumerate(line_items_elem.findall("LineItem"), 1):
            try:
                item = LineItem(
                    id=f"{invoice_id}#{idx}",
                    invoice_id=invoice_id,
                    position_index=idx,
                    description=_get_text(item_elem, "Name"),
                    quantity=_get_text(item_elem, "Quantity"),
                    unit_price=normalize_decimal(_get_text(item_elem, "UnitPrice")),
                    amount=normalize_decimal(_get_text(item_elem, "TotalPrice")),
                )
                line_items.append(item)
            except Exception as e:
                logger.debug(f"Error parsing line item: {e}")
                continue
    
    invoice.line_items = line_items
    
    if not invoice.gross_total:
        logger.warning(f"No gross total for {invoice_number}")
        return None
    
    return invoice


def _get_text(element: ET.Element, tag: str) -> Optional[str]:
    """
    Safely extract text from XML element.
    """
    elem = element.find(tag)
    if elem is not None and elem.text:
        return elem.text.strip()
    return None
