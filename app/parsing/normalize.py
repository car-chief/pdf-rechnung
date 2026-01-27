"""
Normalization utilities for extracted data.
"""
import re
from datetime import datetime
from typing import Optional, Tuple


def normalize_decimal(value: Optional[str]) -> Optional[str]:
    """
    Normalize decimal amounts to string format.
    Handles European (1.234,56) and US (1,234.56) formats.
    Returns Decimal-string or None if parsing fails.
    """
    if not value or not isinstance(value, str):
        return None
    
    value = value.strip()
    if not value:
        return None
    
    # Remove currency symbols and whitespace
    value = re.sub(r'[€$\s]', '', value)
    
    # Try to detect format: European vs US
    # European: 1.234,56 (dot as thousands separator, comma as decimal)
    # US: 1,234.56 (comma as thousands separator, dot as decimal)
    
    comma_count = value.count(',')
    dot_count = value.count('.')
    
    if comma_count == 1 and dot_count == 1:
        # Could be either format - check which separator comes last
        last_comma = value.rfind(',')
        last_dot = value.rfind('.')
        if last_comma > last_dot:
            # European format: 1.234,56
            value = value.replace('.', '').replace(',', '.')
        else:
            # US format: 1,234.56
            value = value.replace(',', '')
    elif comma_count == 1 and dot_count == 0:
        # Only comma - European decimal separator
        value = value.replace(',', '.')
    elif dot_count == 1 and comma_count == 0:
        # Only dot - could be decimal or thousands
        parts = value.split('.')
        if len(parts[1]) == 2 or len(parts[1]) == 3:
            # Likely decimal separator
            pass
        else:
            # Likely thousands separator - remove it
            value = value.replace('.', '')
    elif comma_count > 1:
        # Multiple commas - likely thousands separator (European)
        value = value.replace('.', '').replace(',', '.')
    elif dot_count > 1:
        # Multiple dots - likely thousands separator (US)
        value = value.replace(',', '')
    
    try:
        float_val = float(value)
        # Return as string with 2 decimal places
        return f"{float_val:.2f}"
    except ValueError:
        return None


def normalize_date(value: Optional[str]) -> Optional[str]:
    """
    Normalize date to ISO format (YYYY-MM-DD).
    Handles common formats: DD.MM.YYYY, DD/MM/YYYY, YYYY-MM-DD, etc.
    """
    if not value or not isinstance(value, str):
        return None
    
    value = value.strip()
    if not value:
        return None
    
    # Common date formats to try
    formats = [
        '%d.%m.%Y',    # German: 25.12.2024
        '%d.%m.%y',    # German short: 25.12.24
        '%d/%m/%Y',    # 25/12/2024
        '%d-%m-%Y',    # 25-12-2024
        '%Y-%m-%d',    # ISO: 2024-12-25
        '%Y/%m/%d',    # 2024/12/25
        '%d.%m.',      # German without year: 25.12.
        '%B %d, %Y',   # English: December 25, 2024
        '%b %d, %Y',   # English short: Dec 25, 2024
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    # If no format matched, return None
    return None


def normalize_invoice_number(value: Optional[str]) -> Optional[str]:
    """
    Normalize invoice number (remove extra whitespace).
    """
    if not value or not isinstance(value, str):
        return None
    
    return value.strip() or None


def normalize_vendor(value: Optional[str]) -> Optional[str]:
    """
    Normalize vendor name (trim whitespace, basic cleanup).
    """
    if not value or not isinstance(value, str):
        return None
    
    # Remove extra whitespace
    value = re.sub(r'\s+', ' ', value.strip())
    return value or None


def extract_year_from_path(rel_path: str) -> Optional[int]:
    """
    Extract year from path like 'Rechnungen/2024/file.pdf' or 'Rechnungen\\2024\\file.pdf'.
    Returns int or None if not found.
    """
    # Normalize path separators to forward slashes
    normalized_path = rel_path.replace('\\', '/')
    match = re.search(r'/(\d{4})/', normalized_path)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def is_valid_year(year: Optional[int]) -> bool:
    """Check if year is reasonable (1900-2100)."""
    return year is not None and 1900 <= year <= 2100
