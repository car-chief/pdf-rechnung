"""
Data models and schema definitions for invoices and line items.
"""
from dataclasses import dataclass, asdict
from typing import Optional, List
from enum import Enum
from datetime import date


class ParsingStatus(str, Enum):
    """Status of PDF parsing."""
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    UNSICHER_POSITIONEN = "UNSICHER_POSITIONEN"
    ERROR = "ERROR"


@dataclass
class LineItem:
    """Represents a single line item from an invoice."""
    id: str  # sha256 hash of (invoice_id + position_index)
    invoice_id: str
    position_index: int
    description: str
    quantity: Optional[str] = None
    unit_price: Optional[str] = None
    amount: Optional[str] = None  # Decimal as string
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Invoice:
    """Represents a parsed invoice."""
    id: str  # sha256(rel_path + filehash)
    rel_path: str  # e.g., "Rechnungen/2024/rechnung_001.pdf"
    invoice_year: int  # Extracted from directory path
    invoice_date: Optional[str] = None  # ISO format (YYYY-MM-DD)
    invoice_number: Optional[str] = None
    vendor: Optional[str] = None
    gross_total: Optional[str] = None  # Decimal as string (priority #1)
    net_total: Optional[str] = None  # Optional
    vat_total: Optional[str] = None  # Optional
    currency: str = "EUR"
    status: ParsingStatus = ParsingStatus.SUCCESS
    parsing_notes: str = ""
    file_hash: str = ""
    line_items: List[LineItem] = None
    
    def __post_init__(self):
        if self.line_items is None:
            self.line_items = []
    
    def to_dict(self):
        data = asdict(self)
        # Handle status - ensure it's an enum
        if isinstance(self.status, str):
            data['status'] = self.status
        else:
            data['status'] = self.status.value
        # Handle line_items - convert to dicts if not already
        data['line_items'] = [
            item.to_dict() if hasattr(item, 'to_dict') else item
            for item in self.line_items
        ]
        return data


@dataclass
class IngestIndex:
    """Metadata for incremental parsing."""
    parser_version: str = "1.0.0"
    last_scanned: Optional[str] = None  # ISO format
    files_tracked: dict = None  # {rel_path: {"hash": str, "mtime": float}}
    
    def __post_init__(self):
        if self.files_tracked is None:
            self.files_tracked = {}
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ParsingError:
    """Represents a parsing error for a PDF."""
    id: str  # Same as invoice_id pattern
    rel_path: str
    invoice_year: int
    file_hash: str
    error_message: str
    error_type: str
    timestamp: str  # ISO format
    
    def to_dict(self):
        return asdict(self)
