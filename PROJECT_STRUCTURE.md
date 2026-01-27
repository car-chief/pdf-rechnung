# Projektstruktur - PDF Rechnungen

## Überblick

```
pdf-rechnung/
├── app/                          # FastAPI Applikation
│   ├── main.py                  # Haupteinstieg FastAPI
│   ├── ingest.py                # PDF/XML Ingest-Logik
│   ├── __init__.py
│   ├── parsing/                 # Daten-Parsing Module
│   │   ├── xml_parser.py        # XML zu Invoice Konvertierung
│   │   ├── extract.py           # PDF Text-Extraktion
│   │   ├── normalize.py         # Daten-Normalisierung
│   │   ├── vendors.py           # Vendor-Mapping
│   │   └── __init__.py
│   ├── storage/                 # Datenspeicherung
│   │   ├── json_store.py        # JSON Persistierung
│   │   ├── schema.py            # Datenmodelle (Invoice, LineItem)
│   │   └── __init__.py
│   ├── static/                  # CSS, JavaScript, etc.
│   └── templates/               # HTML Jinja2 Templates
│       ├── base.html
│       ├── index.html
│       ├── detail.html
│       └── errors.html
│
├── data/                        # Datenverzeichnis
│   ├── json/                    # JSON Datenspeicherung
│   │   ├── invoices.json        # Alle importierten Rechnungen
│   │   ├── line_items.json      # Rechnungspositionen
│   │   ├── index.json           # Index-Metadaten
│   │   └── errors.json          # Parse-Fehler
│   └── backups/                 # Daten-Backups
│
├── xml/                         # XML Datenquellen
│   ├── raw/                     # Original XML-Exports
│   │   └── *.xml                # Monatliche Datenexporte
│   └── cleaned/                 # Bereinigte XML-Dateien
│       └── *.xml                # Reduziert auf essenzielle Felder
│
├── scripts/                     # Utility und Debug-Skripte
│   ├── utils/                   # Datenverarbeitung
│   │   ├── clean_xml.py         # XML Bereinigung (Feld-Reduktion)
│   │   └── import_xml_data.py   # XML zu JSON Import
│   └── debug/                   # Entwicklung & Fehlersuche
│       ├── debug_*.py           # Debug-Skripte
│       ├── inspect_pdf.py       # PDF-Struktur-Analyse
│       ├── test_*.py            # Testdateien
│       └── debug_output.txt     # Debug-Ausgaben
│
├── tests/                       # Unit-Tests
│   ├── test_normalize.py        # Normalisierungs-Tests
│   └── __init__.py
│
├── Rechnungen/                  # Archivierte PDF-Rechnungen
│   └── 2025/                    # Nach Jahr organisiert
│       └── *.pdf
│
├── requirements.txt             # Python Dependencies
├── README.md                    # Hauptdokumentation
├── PROJECT_STRUCTURE.md         # Diese Datei
├── Makefile                     # Build/Run-Kommandos
├── QUICKSTART.md                # Schnelleinstieg
├── CHANGELOG.md                 # Version History
└── .gitignore                   # Git Ignore Regeln

```

## Datenfluss

```
Raw XML Export (xml/raw/)
    ↓
Cleanup (scripts/utils/clean_xml.py)
    ↓
Cleaned XML (xml/cleaned/)
    ↓
Parse (app/parsing/xml_parser.py)
    ↓
Invoice Objects (Invoice, LineItem Dataclasses)
    ↓
Import (scripts/utils/import_xml_data.py)
    ↓
JSON Storage (data/json/)
    ↓
FastAPI Server (app/main.py)
    ↓
Web UI (port 8001)
```

## Wichtige Verzeichnisse

### `app/`
Hauptapplikation mit FastAPI-Server und Parsing-Logik.

### `data/json/`
Persistente Speicherung aller Rechnungen und Positionen als JSON.
- `invoices.json`: Alle geparsten Rechnungen
- `line_items.json`: Rechnungspositionen (Produkte)
- `index.json`: Metadaten (last_scanned, parser_version)
- `errors.json`: Parsing-Fehler und Logs

### `xml/`
Datenquellen im XML-Format.
- `raw/`: Original-Exporte (unverändert)
- `cleaned/`: Bereinigte Versionen mit reduzierten Feldern

### `scripts/utils/`
Datenverarbeitung und Import-Automation.
- `clean_xml.py`: Entfernt unnötige XML-Felder (65% Speicherersparnis)
- `import_xml_data.py`: Konvertiert bereinigtes XML in JSON-Datenbank

### `scripts/debug/`
Entwicklung, Debugging und Tests.
- Debug-Skripte für PDF/XML-Analyse
- Unit-Tests
- Fehler-Ausgaben

### `Rechnungen/`
Archivierte PDF-Originaldateien (optional, für Referenz).

## Verwendete Technologien

- **Framework**: FastAPI 0.128.0
- **Server**: Uvicorn 0.40.0
- **Parsing**: xml.etree.ElementTree
- **Daten**: pydantic 2.12.5, dataclasses
- **Templates**: Jinja2 3.1.6
- **Python**: 3.10+

## Nächste Schritte

1. **Weitere XML-Dateien importieren**
   ```bash
   python scripts/utils/clean_xml.py
   python scripts/utils/import_xml_data.py
   ```

2. **Server starten**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

3. **Tests ausführen**
   ```bash
   python -m pytest tests/
   ```

## Pfad-Referenzen in Code

Bei der Aktualisierung von Code beachten:
- `DATA_DIR = Path(__file__).parent.parent / "data"` in `app/main.py`
- `JSONStore(str(DATA_DIR))` verwendet automatisch `data/json/`
- XML-Pfade sind in `scripts/utils/import_xml_data.py` definiert
