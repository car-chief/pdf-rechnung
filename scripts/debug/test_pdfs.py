from pathlib import Path
import traceback
from app.parsing.extract import parse_invoice

REPO_ROOT = Path(__file__).parent
pdfs = list((REPO_ROOT / 'Rechnungen/2025').rglob('*.pdf'))[:3]
for pdf_path in pdfs:
    rel_path = str(pdf_path.relative_to(REPO_ROOT)).replace('\\', '/')
    try:
        invoice, error = parse_invoice(pdf_path, rel_path)
        if error:
            print(f"ERROR {pdf_path.name}: {error}")
        else:
            print(f"OK {pdf_path.name}: gross={invoice.gross_total}")
    except Exception as e:
        print(f"EXCEPTION {pdf_path.name}: {e}")
        traceback.print_exc()
