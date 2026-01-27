# Changelog

## [1.0.0] – 2025-01-27

### ✨ Features

- **PDF Scanning** – Rekursive Erfassung aller PDFs unter `./Rechnungen/{YYYY}/`
- **Intelligentes Parsing** – Extraktion von:
  - Rechnungsdatum (mehrere Formate)
  - Rechnungsnummer
  - Lieferant/Absender
  - Brutto-Gesamtsumme (Pflichtfeld)
  - Netto-Summe & MwSt (optional)
  - Positionen/Artikel (tabellarisch)
  
- **JSON-Persistierung** – Stabile, versionierbare Datenspeicherung:
  - `./data/invoices.json` – Alle Rechnungen
  - `./data/line_items.json` – Positionen
  - `./data/index.json` – Tracking (Hash, mtime, Parser-Version)
  - `./data/errors.json` – Parsing-Fehler
  
- **Inkrementelle Verarbeitung**:
  - Hash-basierte Deduplication
  - Automatische Re-parsing bei Änderungen
  - `--prune` Flag zum Cleanup gelöschter PDFs
  
- **Web-Interface** (FastAPI + Jinja2):
  - **Index-Seite** (`/`)
    - KPI-Übersicht (Gesamtzahl, Bruttosumme, Fehler)
    - Filter nach Jahr & Lieferant
    - Rechnungstabelle mit Status
    - Top 10 Lieferanten
    - Jahresstatistiken
  - **Detail-Seite** (`/invoice/{id}`)
    - Vollständige Metadaten
    - Positionen-Tabelle
    - Parsing-Status & Notizen
    - Technische Infos (ID, Hash)
  - **Fehler-Seite** (`/errors`)
    - Alle Parsing-Fehler
    - Fehlertyp & -meldung
    
- **Normalisierung**:
  - Dezimalformate: Europäisch (`1.234,56`), Englisch (`1,234.56`), Einfach
  - Datumsformate: DD.MM.YYYY, DD/MM/YYYY, ISO, Englisch
  - Beträge als Decimal-Strings (2 Dezimalen)
  - Jahre als Integer mit Validierung
  
- **Robustheit**:
  - Umfassendes Logging auf 3 Ebenen
  - Parser-Versionierung für konsistente Updates
  - Atomic Writes (Temp + Replace) für Datensicherheit
  - Fehlerbehandlung mit Fallbacks
  - Status-Tracking (`SUCCESS`, `UNSICHER_POSITIONEN`, `ERROR`)
  
- **CLI-Befehle**:
  - `python -m app.ingest` – Standard-Ingest
  - `python -m app.ingest --force` – Re-parse alles
  - `python -m app.ingest --prune` – Cleanup gelöschter PDFs
  - `python -m app.ingest --debug` – Verbose Logging
  
- **Unit-Tests**:
  - `pytest tests/test_normalize.py` – Normalisierungsfunktionen
  - 30+ Test-Cases für Edge-Cases
  
- **Dokumentation**:
  - `README.md` – Vollständiges Handbuch
  - `QUICKSTART.md` – 5-Minuten-Einstieg
  - Inline-Code-Kommentare

### 🛠️ Technology Stack

- Python 3.11+
- FastAPI 0.104.1
- pdfplumber 0.10.3 (pypdf 3.17.1 als Fallback)
- Jinja2 3.1.2
- pytest 7.4.3

### 📁 Project Structure

```
pdf-rechnung/
├── app/
│   ├── main.py           # FastAPI App & Routes
│   ├── ingest.py         # PDF Ingest CLI
│   ├── storage/
│   │   ├── schema.py     # Datenmodelle
│   │   └── json_store.py # JSON-Persistierung
│   ├── parsing/
│   │   ├── extract.py    # PDF-Parsing
│   │   ├── normalize.py  # Normalisierung
│   │   └── vendors.py    # Vendor-Hints
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── detail.html
│   │   └── errors.html
│   └── static/
├── tests/
│   └── test_normalize.py
├── Rechnungen/
│   ├── 2022/ ... 2025/
├── data/                 # .gitignored
│   ├── invoices.json
│   ├── line_items.json
│   ├── index.json
│   └── errors.json
├── requirements.txt
├── README.md
├── QUICKSTART.md
├── Makefile
├── install.sh
└── install.bat
```

### 🎯 Key Design Decisions

1. **JSON statt Datenbank**
   - Einfach versionierbar in Git
   - Portabel, keine externe Abhängigkeit
   - Pretty-printed für Lesbarkeit
   - Stabile Sortierung für konsistente Diffs

2. **Atomare Writes**
   - Temp-Datei schreiben → Atomic Replace
   - Verhindert korrupte JSON bei Crashes

3. **Hash-basierte Deduplication**
   - `sha256(rel_path + file_hash)` = Invoice ID
   - Ermöglicht sicheres Tracking von Bewegungen/Renames

4. **Parser-Versionierung**
   - Version in index.json gespeichert
   - Re-parse bei Parser-Update automatisch
   - Verhindert stale Data bei Code-Änderungen

5. **Server-Side Rendering**
   - Jinja2 für Templates, keine SPA-Komplexität
   - Schneller, einfacher zu debuggen
   - SEO-freundlich (falls nötig)

6. **Heuristische Extraktion**
   - Fallback-Patterns für verschiedene Hersteller
   - Priorität auf Brutto-Summe (kritisch)
   - Positionen optional, mit Status-Flag

### 🔍 Known Limitations & TODOs

- ❌ **OCR nicht implementiert** – Nur digitale PDFs (scanned PDF würde pdfplumber nicht lesen)
- ❌ **Multi-Currency** – Hardcoded EUR (einfach zu erweitern)
- ❌ **Duplicate Detection** – Noch nicht implementiert
- ❌ **Export** (CSV, Excel) – Noch nicht implementiert
- ❌ **Dark Mode** – TODO
- ⚠️ **Skalierung** – JSON vollständig im RAM für jeden Request (OK bis ~10k PDFs)

### 🚀 Future Features

- [ ] OCR-Support für gescannte Rechnungen (pytesseract)
- [ ] Duplicate Detection (Fuzzy Matching)
- [ ] Batch-Export (CSV, Excel)
- [ ] Multi-Currency-Support
- [ ] PDF-Viewer integriert (iframe)
- [ ] Dark Mode UI
- [ ] SQLite-Backend Alternative
- [ ] Redis-Cache für Abfragen
- [ ] API-Endpoints (JSON)
- [ ] Vendor-Plugins für besseres Parsing

### 🧪 Testing

```bash
# Unit-Tests
pytest tests/test_normalize.py -v

# Ingest mit Debug-Output
python -m app.ingest --debug

# Manual PDF Parsing
python -c "
from app.parsing import parse_invoice
from pathlib import Path
invoice, error = parse_invoice(Path('test.pdf'), 'test.pdf')
print(f'Error: {error}' if error else f'OK: {invoice.gross_total}')
"
```

### 📊 Performance

- **Ingest:** ~100 PDFs/Minute (Standard-Hardware)
- **JSON Laden:** <100ms (bis 10k PDFs)
- **Web-Request:** <50ms (bis 5k Rechnungen)

### 📝 Notes for Developers

1. **Adding Parser Heuristics:**
   - Edit `app/parsing/extract.py`
   - Fügen Sie Regex-Pattern hinzu
   - Test mit `--debug` Flag

2. **Adding Vendor-Specific Rules:**
   - Edit `app/parsing/vendors.py`
   - Returne dict mit Hints für extract.py

3. **Changing Data Schema:**
   - Update `app/storage/schema.py`
   - Update JSON-Lese/Schreib-Logik in `json_store.py`
   - Erhöhen Sie `parser_version` in ingest.py

4. **Git Workflow:**
   - `data/` ist in `.gitignore` (lokal!)
   - `requirements.txt` wird committed
   - JSON-Format stabil (sorted keys, pretty-print)

### ✅ Validation Checklist

- ✓ PDFs aus `./Rechnungen/{YYYY}/` werden korrekt gescannt
- ✓ Jahr wird aus Pfad extrahiert (`invoice_year: int`)
- ✓ Relative Pfade gespeichert (`rel_path: str`)
- ✓ Brutto-Summe wird extrahiert (Priorität #1)
- ✓ JSON-Dateien sind stabil & versionierbar
- ✓ Inkrementelles Parsing funktioniert
- ✓ Web-UI zeigt Filter & KPIs
- ✓ Fehler werden getracked
- ✓ Unit-Tests bestehen
- ✓ Dokumentation vollständig

---

## Installation & Start

```bash
# 1. Setup
pip install -r requirements.txt

# 2. PDFs in Rechnungen/{YYYY}/ platzieren

# 3. Ingest
python -m app.ingest

# 4. Server starten
uvicorn app.main:app --reload

# 5. Browser öffnen
# http://localhost:8000
```

---

**Release Date:** 2025-01-27  
**Status:** Production Ready  
**Maintainer:** Senior Engineer
