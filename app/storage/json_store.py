"""
JSON-based persistent storage for invoices.
Handles atomic writes and incremental updates.
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
import tempfile
import shutil
from .schema import Invoice, LineItem, IngestIndex, ParsingError, ParsingStatus


class JSONStore:
    """Handles JSON persistence with atomic writes."""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir) / "json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.invoices_file = self.data_dir / "invoices.json"
        self.line_items_file = self.data_dir / "line_items.json"
        self.index_file = self.data_dir / "index.json"
        self.errors_file = self.data_dir / "errors.json"
        
        # Initialize files if they don't exist
        self._init_files()
    
    def _init_files(self):
        """Create empty JSON files if they don't exist."""
        if not self.invoices_file.exists():
            self._atomic_write(self.invoices_file, [])
        if not self.line_items_file.exists():
            self._atomic_write(self.line_items_file, [])
        if not self.errors_file.exists():
            self._atomic_write(self.errors_file, [])
        if not self.index_file.exists():
            index = IngestIndex()
            self._atomic_write(self.index_file, index.to_dict())
    
    def _atomic_write(self, filepath: Path, data):
        """Write JSON file atomically (temp + replace)."""
        # Convert objects to dicts if needed
        if isinstance(data, list):
            serializable = [
                item.to_dict() if hasattr(item, 'to_dict') else item
                for item in data
            ]
        elif hasattr(data, 'to_dict'):
            serializable = data.to_dict()
        else:
            serializable = data
        
        # Write to temp file first
        temp_fd, temp_path = tempfile.mkstemp(dir=self.data_dir, suffix='.tmp')
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(serializable, f, indent=2, ensure_ascii=False, sort_keys=True)
            # Atomic replace
            shutil.move(temp_path, filepath)
        except Exception as e:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
    
    def load_invoices(self) -> List[Invoice]:
        """Load all invoices from JSON."""
        try:
            with open(self.invoices_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            invoices = []
            for item in data:
                invoice = Invoice(**item)
                invoices.append(invoice)
            return invoices
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def load_line_items(self) -> List[LineItem]:
        """Load all line items from JSON."""
        try:
            with open(self.line_items_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            items = []
            for item_data in data:
                item = LineItem(**item_data)
                items.append(item)
            return items
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def load_errors(self) -> List[ParsingError]:
        """Load all parsing errors from JSON."""
        try:
            with open(self.errors_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            errors = []
            for item_data in data:
                error = ParsingError(**item_data)
                errors.append(error)
            return errors
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def load_index(self) -> IngestIndex:
        """Load ingest index."""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return IngestIndex(**data)
        except (FileNotFoundError, json.JSONDecodeError):
            return IngestIndex()
    
    def save_invoices(self, invoices: List[Invoice]):
        """Save invoices to JSON (sorted by id for stable output)."""
        sorted_invoices = sorted(invoices, key=lambda x: x.id)
        self._atomic_write(self.invoices_file, sorted_invoices)
    
    def save_line_items(self, line_items: List[LineItem]):
        """Save line items to JSON (sorted by id for stable output)."""
        sorted_items = sorted(line_items, key=lambda x: x.id)
        self._atomic_write(self.line_items_file, sorted_items)
    
    def save_errors(self, errors: List[ParsingError]):
        """Save parsing errors to JSON (sorted by id for stable output)."""
        sorted_errors = sorted(errors, key=lambda x: x.id)
        self._atomic_write(self.errors_file, sorted_errors)
    
    def save_index(self, index: IngestIndex):
        """Save ingest index."""
        self._atomic_write(self.index_file, index)
    
    def add_or_update_invoice(self, invoice: Invoice):
        """Add or update a single invoice."""
        invoices = self.load_invoices()
        
        # Remove existing invoice with same id if exists
        invoices = [inv for inv in invoices if inv.id != invoice.id]
        
        # Add new invoice
        invoices.append(invoice)
        self.save_invoices(invoices)
    
    def add_or_update_error(self, error: ParsingError):
        """Add or update a single parsing error."""
        errors = self.load_errors()
        
        # Remove existing error with same id if exists
        errors = [err for err in errors if err.id != error.id]
        
        # Add new error
        errors.append(error)
        self.save_errors(errors)
    
    def remove_invoice(self, invoice_id: str):
        """Remove invoice and its line items."""
        invoices = self.load_invoices()
        invoices = [inv for inv in invoices if inv.id != invoice_id]
        self.save_invoices(invoices)
        
        # Remove associated line items
        line_items = self.load_line_items()
        line_items = [item for item in line_items if item.invoice_id != invoice_id]
        self.save_line_items(line_items)
    
    def remove_error(self, error_id: str):
        """Remove a single parsing error."""
        errors = self.load_errors()
        errors = [err for err in errors if err.id != error_id]
        self.save_errors(errors)
    
    def invoice_exists(self, invoice_id: str) -> bool:
        """Check if invoice already exists."""
        invoices = self.load_invoices()
        return any(inv.id == invoice_id for inv in invoices)
    
    def get_invoice_by_path(self, rel_path: str) -> Optional[Invoice]:
        """Get invoice by relative path."""
        invoices = self.load_invoices()
        for inv in invoices:
            if inv.rel_path == rel_path:
                return inv
        return None
    
    def prune_missing_invoices(self, existing_rel_paths: set):
        """Remove invoices whose PDF files no longer exist."""
        invoices = self.load_invoices()
        errors = self.load_errors()
        
        # Filter invoices that still exist
        removed_ids = set()
        invoices_to_keep = []
        for inv in invoices:
            if inv.rel_path in existing_rel_paths:
                invoices_to_keep.append(inv)
            else:
                removed_ids.add(inv.id)
        
        # Filter errors for removed invoices
        errors_to_keep = [err for err in errors if err.id not in removed_ids]
        
        # Filter line items
        line_items = self.load_line_items()
        line_items_to_keep = [item for item in line_items if item.invoice_id not in removed_ids]
        
        self.save_invoices(invoices_to_keep)
        self.save_errors(errors_to_keep)
        self.save_line_items(line_items_to_keep)
        
        return len(removed_ids)
