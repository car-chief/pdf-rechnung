"""
Ingest command to scan and parse invoices.
"""
import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
import os

from .storage import JSONStore, ParsingError
from .parsing import parse_invoice, compute_file_hash, compute_invoice_id

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


PARSER_VERSION = "1.0.0"
REPO_ROOT = Path(__file__).parent.parent
RECHNUNGEN_DIR = REPO_ROOT / "Rechnungen"


def find_all_pdfs(base_dir: Path = RECHNUNGEN_DIR) -> list:
    """
    Recursively find all PDF files under base_dir.
    Returns list of (absolute_path, relative_path) tuples.
    
    relative_path format: "Rechnungen/2024/file.pdf"
    """
    pdfs = []
    
    if not base_dir.exists():
        logger.warning(f"Rechnungen directory not found: {base_dir}")
        return pdfs
    
    for pdf_path in base_dir.rglob("*.pdf"):
        try:
            rel_path = pdf_path.relative_to(REPO_ROOT)
            # Normalize path separators to forward slashes
            rel_path_str = str(rel_path).replace("\\", "/")
            pdfs.append((pdf_path, rel_path_str))
        except ValueError:
            logger.warning(f"Could not compute relative path for {pdf_path}")
    
    return sorted(pdfs)


def should_reparse(rel_path: str, file_hash: str, stored_index: dict) -> bool:
    """
    Determine if a PDF should be reparsed.
    
    Skip if:
    - Same hash AND parser version hasn't changed
    
    Reparse if:
    - Hash changed
    - Parser version changed
    - Not in index yet
    """
    if rel_path not in stored_index:
        return True
    
    stored_info = stored_index[rel_path]
    
    if stored_info.get("hash") != file_hash:
        logger.info(f"File hash changed: {rel_path}")
        return True
    
    if stored_info.get("parser_version") != PARSER_VERSION:
        logger.info(f"Parser version changed: {rel_path}")
        return True
    
    return False


def ingest_pdfs(force: bool = False, prune: bool = False, debug: bool = False, data_dir: str = "./data"):
    """
    Main ingest logic.
    
    Args:
        force: Re-parse all PDFs regardless of hash/version
        prune: Remove JSON entries for deleted PDFs
        debug: Verbose logging
        data_dir: Path to data directory for JSON files
    """
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    store = JSONStore(data_dir)
    
    logger.info(f"Scanning PDFs in {RECHNUNGEN_DIR}")
    pdfs = find_all_pdfs()
    logger.info(f"Found {len(pdfs)} PDF(s)")
    
    if not pdfs:
        logger.warning("No PDFs found!")
        return
    
    # Load current state
    existing_invoices = store.load_invoices()
    existing_line_items = store.load_line_items()
    existing_errors = store.load_errors()
    index = store.load_index()
    
    stats = {
        "total": len(pdfs),
        "parsed": 0,
        "skipped": 0,
        "errors": 0,
        "updated": 0,
    }
    
    # Track which files we've seen (for pruning)
    seen_rel_paths = set()
    
    for abs_path, rel_path in pdfs:
        try:
            seen_rel_paths.add(rel_path)
            file_hash = compute_file_hash(abs_path)
            
            # Check if we should reparse
            if not force and not should_reparse(rel_path, file_hash, index.files_tracked):
                logger.debug(f"Skipping (unchanged): {rel_path}")
                stats["skipped"] += 1
                continue
            
            # Parse invoices (may be multiple per PDF)
            logger.info(f"Parsing: {rel_path}")
            invoices, error_msg = parse_invoice(abs_path, rel_path)
            
            if error_msg:
                # Store error
                logger.error(f"Parse error: {rel_path} - {error_msg}")
                invoice_id = compute_invoice_id(rel_path, file_hash)
                error = ParsingError(
                    id=invoice_id,
                    rel_path=rel_path,
                    invoice_year=_extract_year_from_path(rel_path) or 0,
                    file_hash=file_hash,
                    error_message=error_msg,
                    error_type="parse_error",
                    timestamp=datetime.utcnow().isoformat(),
                )
                store.add_or_update_error(error)
                stats["errors"] += 1
                continue
            
            # Process each invoice
            for invoice in invoices:
                # Check if this is an update
                existing = store.get_invoice_by_path(rel_path)
                if existing and existing.id != invoice.id:
                    logger.info(f"Updated: {rel_path} - {invoice.invoice_number}")
                    stats["updated"] += 1
                    # Remove old invoice and line items
                    store.remove_invoice(existing.id)
                
                # Save invoice and line items
                store.add_or_update_invoice(invoice)
                if invoice.line_items:
                    existing_line_items = [
                        item for item in existing_line_items
                        if item.invoice_id != invoice.id
                    ]
                    existing_line_items.extend(invoice.line_items)
                    store.save_line_items(existing_line_items)
                
                # Remove error if it existed
                store.remove_error(invoice.id)
                
                stats["parsed"] += 1
            
            # Update index for this PDF file
            index.files_tracked[rel_path] = {
                "hash": file_hash,
                "mtime": os.path.getmtime(abs_path),
                "parser_version": PARSER_VERSION,
            }
            
        except Exception as e:
            logger.error(f"Unexpected error processing {rel_path}: {e}", exc_info=debug)
            stats["errors"] += 1
    
    # Save updated index
    index.last_scanned = datetime.utcnow().isoformat()
    store.save_index(index)
    
    # Prune deleted files if requested
    if prune:
        logger.info("Pruning deleted invoices...")
        removed_count = store.prune_missing_invoices(seen_rel_paths)
        logger.info(f"Removed {removed_count} invoice(s) for deleted PDFs")
    
    # Log summary
    logger.info("\n" + "="*50)
    logger.info(f"Ingest Summary:")
    logger.info(f"  Total PDFs: {stats['total']}")
    logger.info(f"  Parsed: {stats['parsed']}")
    logger.info(f"  Updated: {stats['updated']}")
    logger.info(f"  Skipped: {stats['skipped']}")
    logger.info(f"  Errors: {stats['errors']}")
    logger.info(f"  Data directory: {store.data_dir}")
    logger.info("="*50)


def _extract_year_from_path(rel_path: str) -> int:
    """Extract year from path, handles both / and \\ separators."""
    import re
    normalized_path = rel_path.replace('\\', '/')
    match = re.search(r'/(\d{4})/', normalized_path)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass
    return 0


def main():
    """Entry point for ingest command."""
    parser = argparse.ArgumentParser(description="Ingest PDFs and extract invoice data")
    parser.add_argument("--force", action="store_true", help="Re-parse all PDFs")
    parser.add_argument("--prune", action="store_true", help="Remove entries for deleted PDFs")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--data-dir", default="./data", help="Data directory for JSON files")
    
    args = parser.parse_args()
    
    try:
        ingest_pdfs(
            force=args.force,
            prune=args.prune,
            debug=args.debug,
            data_dir=args.data_dir,
        )
    except KeyboardInterrupt:
        logger.info("Ingest interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
