"""
PDF parsing and data extraction using pdfplumber.
"""
import logging
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import hashlib

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from .normalize import (
    normalize_decimal,
    normalize_date,
    normalize_invoice_number,
    normalize_vendor,
    extract_year_from_path,
    is_valid_year,
)
from ..storage.schema import Invoice, LineItem, ParsingStatus

logger = logging.getLogger(__name__)


def compute_file_hash(filepath: Path) -> str:
    """Compute SHA256 hash of PDF file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_invoice_id(rel_path: str, file_hash: str) -> str:
    """
    Compute invoice ID from relative path and file hash.
    invoice_id = sha256(rel_path + file_hash)
    """
    combined = rel_path + file_hash
    return hashlib.sha256(combined.encode()).hexdigest()


def extract_text_from_pdf(filepath: Path) -> str:
    """
    Extract all text from PDF.
    """
    if not pdfplumber:
        raise ImportError("pdfplumber is required for PDF parsing")
    
    try:
        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
                text += "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {filepath}: {e}")
        raise


def extract_tables_from_pdf(filepath: Path) -> List[List[List[str]]]:
    """
    Extract all tables from PDF using pdfplumber.
    Returns list of tables, each table is list of rows, each row is list of cells.
    """
    if not pdfplumber:
        return []
    
    try:
        tables = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
        return tables
    except Exception as e:
        logger.warning(f"Error extracting tables from {filepath}: {e}")
        return []


def parse_invoice(filepath: Path, rel_path: str) -> Tuple[List[Invoice], Optional[str]]:
    """
    Parse a single PDF which may contain multiple invoices.
    
    Returns:
        (List of Invoice objects, error_message)
        - If error_message is not None, general parsing failed
        - Individual invoices may still have partial errors but are returned
    """
    try:
        # Extract year from path
        invoice_year = extract_year_from_path(rel_path)
        if not is_valid_year(invoice_year):
            return [], f"Invalid year in path: {rel_path}"
        
        # Extract full text from PDF
        try:
            full_text = extract_text_from_pdf(filepath)
        except Exception as e:
            return [], f"Failed to extract text: {str(e)}"
        
        # Split PDF into invoice sections by invoice number
        invoice_sections = _split_pdf_by_invoices(full_text)
        
        if not invoice_sections:
            return [], "No invoices found in PDF"
        
        # Parse each section as a separate invoice
        invoices = []
        seen_invoice_numbers = set()
        
        for section_text in invoice_sections:
            try:
                # Extract invoice number
                invoice_number = _extract_invoice_number(section_text)
                if not invoice_number:
                    logger.debug(f"No invoice number found in section, skipping")
                    continue
                
                # Skip duplicates
                if invoice_number in seen_invoice_numbers:
                    logger.info(f"Duplicate invoice number {invoice_number}, skipping")
                    continue
                
                seen_invoice_numbers.add(invoice_number)
                
                # Compute file hash (same for all invoices from this PDF)
                file_hash = compute_file_hash(filepath)
                
                # Create unique invoice ID based on invoice number
                invoice_id = hashlib.sha256(
                    f"{invoice_number}_{file_hash}".encode()
                ).hexdigest()
                
                # Create invoice object
                invoice = Invoice(
                    id=invoice_id,
                    rel_path=rel_path,
                    invoice_year=invoice_year,
                    file_hash=file_hash,
                )
                
                # Extract fields from section
                invoice.invoice_number = invoice_number
                invoice.invoice_date = _extract_date(section_text)
                invoice.vendor = _extract_vendor(full_text)  # Vendor from full PDF
                invoice.gross_total, vat_amount = _extract_gross_total(section_text)
                invoice.net_total = _extract_net_total(section_text)
                invoice.vat_total = vat_amount
                
                # Check critical fields
                if not invoice.gross_total:
                    logger.warning(f"Could not extract gross total for {invoice_number}")
                    invoice.status = ParsingStatus.UNSICHER_BETRAG
                    invoice.parsing_notes = "Could not extract gross total"
                
                invoices.append(invoice)
                logger.debug(f"Parsed invoice: {invoice_number}")
                
            except Exception as e:
                logger.debug(f"Error parsing invoice section: {e}")
                continue
        
        if not invoices:
            return [], "Could not parse any invoices from PDF"
        
        return invoices, None
        
    except Exception as e:
        logger.error(f"Unexpected error parsing {rel_path}: {e}", exc_info=True)
        return [], f"Unexpected error: {str(e)}"


def _split_pdf_by_invoices(full_text: str) -> List[str]:
    """
    Split PDF text by invoice numbers.
    Returns list of invoice text sections.
    """
    import re
    
    # Find all invoice number patterns
    # Matches: "Rechnung-Nr.: SR25-00686" or similar variations
    pattern = r'Rechnung[s]?[-_\s]*Nr\.?[:\s]+([A-Za-z0-9\-/_]+)'
    
    matches = list(re.finditer(pattern, full_text, re.IGNORECASE))
    
    if not matches:
        # No invoice numbers found, return whole text as one section
        return [full_text]
    
    # Extract sections between invoice numbers
    sections = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        section = full_text[start:end]
        sections.append(section)
    
    return sections


def _extract_date(text: str) -> Optional[str]:
    """
    Extract invoice date from text.
    Looks for common patterns like "Rechnungsdatum" or "Datum".
    """
    import re
    
    # Common German patterns
    patterns = [
        r'Rechnungsdatum\D+(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})',
        r'Datum\D+(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})',
        r'Rechnung.*?(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})',
        r'Invoice Date.*?(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})',
        r'(\d{1,2}\.\d{1,2}\.\d{4})',  # DD.MM.YYYY format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            normalized = normalize_date(date_str)
            if normalized:
                return normalized
    
    return None


def _extract_invoice_number(text: str) -> Optional[str]:
    """
    Extract invoice number from text.
    """
    import re
    
    patterns = [
        r'Rechnungsnummer\D+([A-Za-z0-9\-/]+)',
        r'Rechnung\s*[Nn]r\.?\D+([A-Za-z0-9\-/]+)',
        r'Invoice\s*[Nn]o\.?\D+([A-Za-z0-9\-/]+)',
        r'Rechnungs\s*Nr\.?\D+([A-Za-z0-9\-/]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            inv_num = match.group(1).strip()
            normalized = normalize_invoice_number(inv_num)
            if normalized:
                return normalized
    
    return None


def _extract_vendor(text: str) -> Optional[str]:
    """
    Extract vendor/supplier name from text.
    Usually near the top of the invoice (sender info).
    """
    lines = text.split('\n')
    
    # Heuristic: First few non-empty lines often contain vendor name
    for i, line in enumerate(lines[:30]):
        line_stripped = line.strip()
        # Skip short lines, page numbers, etc.
        if len(line_stripped) > 5 and len(line_stripped) < 100:
            # Skip common header words
            if not any(word in line_stripped.lower() for word in 
                      ['rechnung', 'invoice', 'page', 'seite', 'date', 'datum']):
                return normalize_vendor(line_stripped)
    
    return None


def _extract_gross_total(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract gross total (Endsumme, Gesamtbetrag) from text.
    Also attempts to extract VAT amount.
    
    Returns: (gross_total, vat_amount)
    """
    import re
    
    # Patterns for gross total
    gross_patterns = [
        r'(?:Gesamtbetrag|Endsumme|Gesamtsumme|Total|Grand Total|Summe)[:\s]+([€\d.,\-\s]+)',
        r'(?:Zu zahlen|To pay)[:\s]+([€\d.,\-\s]+)',
        r'(?:Rechnungssum|Invoice Total)[:\s]+([€\d.,\-\s]+)',
    ]
    
    for pattern in gross_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Take the last match (usually the final total)
            amount_str = matches[-1]
            normalized = normalize_decimal(amount_str)
            if normalized:
                # Try to extract VAT
                vat = _extract_vat_amount(text)
                return normalized, vat
    
    return None, None


def _extract_vat_amount(text: str) -> Optional[str]:
    """
    Extract VAT amount from text.
    """
    import re
    
    patterns = [
        r'(?:MwSt|Mehrwertsteuer|VAT|USt)[:\s]+([€\d.,\-\s]+)',
        r'(?:Steuerbetrag)[:\s]+([€\d.,\-\s]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1)
            normalized = normalize_decimal(amount_str)
            if normalized:
                return normalized
    
    return None


def _extract_net_total(text: str) -> Optional[str]:
    """
    Extract net total (without VAT) from text.
    """
    import re
    
    patterns = [
        r'(?:Nettobetrag|Subtotal|Zwischensumme)[:\s]+([€\d.,\-\s]+)',
        r'(?:Netto)[:\s]+([€\d.,\-\s]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1)
            normalized = normalize_decimal(amount_str)
            if normalized:
                return normalized
    
    return None


def _extract_line_items_from_tables(invoice_id: str, tables: List) -> List[LineItem]:
    """
    Extract line items from PDF tables.
    """
    items = []
    
    if not tables:
        return items
    
    # Process each table
    for table in tables:
        if not table or len(table) < 2:
            continue
        
        try:
            # Try to identify header row
            header_row = table[0]
            is_header = any(
                keyword in _safe_str(cell).lower()
                for cell in header_row
                for keyword in ['position', 'beschreibung', 'menge', 'preis', 'betrag',
                              'description', 'qty', 'quantity', 'amount', 'total']
            )
            
            if not is_header:
                continue
            
            # Process data rows
            start_idx = 1
            for row_idx, row in enumerate(table[start_idx:], start=start_idx):
                if len(row) < 2:
                    continue
                
                # Skip empty rows
                if all(not _safe_str(cell) for cell in row):
                    continue
                
                try:
                    item = LineItem(
                        id="",  # Will be set below
                        invoice_id=invoice_id,
                        position_index=row_idx,
                        description=_safe_str(row[0]),
                        quantity=_safe_str(row[1]) if len(row) > 1 else None,
                        unit_price=_safe_decimal(row[2]) if len(row) > 2 else None,
                        amount=_safe_decimal(row[-1]) if len(row) > 3 else None,
                    )
                    
                    # Compute item ID
                    item_hash_input = f"{invoice_id}#{row_idx}"
                    item.id = hashlib.sha256(item_hash_input.encode()).hexdigest()
                    
                    items.append(item)
                except Exception as row_error:
                    logger.debug(f"Error processing row {row_idx}: {row_error}")
                    continue
        except Exception as e:
            logger.debug(f"Error processing table: {e}")
            continue
    
    return items


def _safe_str(value) -> str:
    """Safely convert value to string, handling various types."""
    if value is None:
        return ""
    
    # If already a string, just strip and return
    if isinstance(value, str):
        return value.strip()
    
    # Handle dict-like objects (pdfplumber cells in older versions)
    if isinstance(value, dict):
        # Try common keys for cell values in different pdfplumber versions
        for key in ['value', 'text', 'content', 'char']:
            if key in value and value[key] is not None:
                value = value[key]
                break
        else:
            value = str(value)
    
    # Convert to string and strip
    try:
        s = str(value).strip()
        return s if s else ""
    except Exception:
        return ""


def _safe_decimal(value) -> Optional[str]:
    """Safely convert value to decimal string."""
    s = _safe_str(value)
    if not s:
        return None
    return normalize_decimal(s)
