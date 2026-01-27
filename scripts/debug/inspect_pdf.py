#!/usr/bin/env python3
"""
Inspect PDF structure to understand invoice separation.
"""
import pdfplumber
from pathlib import Path

# Inspect the two example PDFs
pdf_files = [
    "Rechnungen/2025/documents - 2025-07-09T091659.254.pdf",  # mehrere Rechnungen
]

for pdf_path in pdf_files:
    full_path = Path(pdf_path)
    if not full_path.exists():
        print(f"File not found: {pdf_path}")
        continue
    
    print(f"\n{'='*70}")
    print(f"Analyzing: {pdf_path}")
    print(f"{'='*70}\n")
    
    with pdfplumber.open(full_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}\n")
        
        # Extract text from all pages
        full_text = ""
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            print(f"--- PAGE {page_num} ---")
            print(text[:500] if text else "(no text)")
            print()
            full_text += f"\n[PAGE {page_num}]\n{text}\n"
        
        # Search for invoice numbers
        import re
        print(f"\n{'='*70}")
        print("SEARCHING FOR INVOICE NUMBERS")
        print(f"{'='*70}\n")
        
        patterns = [
            (r'Rechnungsnummer[:\s]+([A-Za-z0-9\-/_]+)', 'Rechnungsnummer'),
            (r'Rechnung[s]?[-_\s]*Nr\.?[:\s]+([A-Za-z0-9\-/_]+)', 'Rechnung Nr.'),
            (r'Invoice\s*No\.?[:\s]+([A-Za-z0-9\-/_]+)', 'Invoice No'),
            (r'Rechnungs[_\s]?Nr[_\s]?[:\s]*([A-Za-z0-9\-/_]+)', 'Rechnungs Nr'),
            (r'SR\d+[\-_]?\d+', 'SR pattern'),
            (r'INV[\-_]?\d+', 'INV pattern'),
        ]
        
        found_invoices = {}
        for pattern, label in patterns:
            matches = re.finditer(pattern, full_text, re.IGNORECASE)
            for match in matches:
                # Handle both group(1) and group(0) depending on pattern
                inv_num = match.group(1).strip() if match.lastindex else match.group(0).strip()
                # Get context (200 chars before and after)
                start = max(0, match.start() - 200)
                end = min(len(full_text), match.end() + 300)
                context = full_text[start:end].replace('\n', ' ')
                
                if inv_num not in found_invoices:
                    found_invoices[inv_num] = (label, context)
                    print(f"Found {label}: {inv_num}")
                    print(f"Context: ...{context}...\n")
        
        print(f"\nTotal unique invoice numbers found: {len(found_invoices)}")
        
        # Search for amounts
        print(f"\n{'='*70}")
        print("SEARCHING FOR AMOUNTS")
        print(f"{'='*70}\n")
        
        amount_patterns = [
            r'(?:Gesamtbetrag|Gesamtsumme|Endsumme)[:\s]+([€\d.,\-\s]+)',
            r'(?:Zu zahlender Betrag|Total)[:\s]+([€\d.,\-\s]+)',
        ]
        
        for pattern in amount_patterns:
            matches = re.finditer(pattern, full_text, re.IGNORECASE)
            for match in matches:
                amount = match.group(1).strip()
                print(f"Found amount: {amount}")
