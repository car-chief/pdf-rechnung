import traceback
import logging
logging.basicConfig(level=logging.DEBUG)

from pathlib import Path
from app.parsing.extract import parse_invoice

pdf_path = Path('Rechnungen/2025/documents - 2025-01-06T102331.808.pdf')
rel_path = 'Rechnungen/2025/documents - 2025-01-06T102331.808.pdf'

try:
    print("Calling parse_invoice...")
    invoice, error = parse_invoice(pdf_path, rel_path)
    print(f"Result: invoice={invoice}, error={error}")
    if error:
        print(f'Error: {error}')
except Exception as e:
    print(f'Exception: {e}')
    traceback.print_exc()
