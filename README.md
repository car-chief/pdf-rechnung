# PDF Rechnungen

Lokale Web-Übersicht zur Verwaltung und Analyse von Rechnungen. **Keine Cloud, keine externen APIs** – alles lokal und versionierbar.

Unterstützt sowohl **PDF-Dateien** als auch **XML-Exporte** als Datenquellen.

## 🌟 Features

✅ **Datenquellen-Flexibilität** – PDF-Extraktion ODER XML-Import  
✅ **Automatisches Scanning** – Rekursive Erfassung aller PDFs/XMLs  
✅ **Intelligentes Parsing** – Extraktion von Datum, Nummer, Lieferant, Summe  
✅ **JSON-Persistenz** – Stabile Speicherung, versionierbar  
✅ **Web-Interface** – FastAPI + Jinja2, responsive Design  
✅ **Filtering & KPIs** – Nach Jahr, Monat, Lieferant mit Statistiken  
✅ **Fehlerbehandlung** – Dedizierte Error-Seite mit Parsing-Logs  

## 🏗️ Projektstruktur

```
pdf-rechnung/
├── app/                      FastAPI Applikation
│   ├── parsing/              PDF/XML Parsing
│   ├── storage/              JSON Persistierung
│   ├── templates/            HTML Templates
│   └── main.py               FastAPI Server
├── data/
│   ├── json/                 Datenbank (invoices.json, line_items.json)
│   └── backups/              Automatische Backups
├── xml/
│   ├── raw/                  Original XML-Exporte
│   └── cleaned/              Bereinigte XML-Dateien
├── scripts/
│   ├── utils/                Datenverarbeitung
│   └── debug/                Debug-Tools
├── tests/                    Unit Tests
└── Rechnungen/               PDF Archive (Jahr-basiert)
```

📖 Ausführliche Struktur-Dokumentation: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 📋 Technologie

- **Python 3.10+**
- **FastAPI 0.128.0** – Web-Framework
- **pdfplumber, pypdf** – PDF-Extraktion
- **xml.etree.ElementTree** – XML-Parsing
- **Jinja2 3.1.6** – Template-Rendering
- **pydantic 2.12.5** – Datenvalidierung

## 🚀 Schnelleinstieg

### 1. Setup

```bash
cd pdf-rechnung
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. Daten importieren

**Optionale Datenquellen-Vorbereitung:**

```bash
# XML bereinigen (optional, falls zu groß)
python scripts/utils/clean_xml.py

# Rechnungen aus XML importieren
python scripts/utils/import_xml_data.py
```

### 3. Server starten

```bash
python -m uvicorn app.main:app --reload
```

Öffnen Sie: **http://127.0.0.1:8000**

## 📁 Datenverwaltung

### Datenbank-Struktur

```
data/json/
├── invoices.json      Alle importierten Rechnungen
├── line_items.json    Rechnungspositionen
├── index.json         Metadaten (last_scanned, parser_version)
└── errors.json        Parse-Fehler
```

### Datenquellen

```
xml/raw/               Original XML-Exporte (groß, nicht versioniert)
xml/cleaned/           Bereinigte XMLs (klein, versionierbar)
Rechnungen/2025/       PDF-Archive (optional)
```

## 🛠️ Verwaltungs-Commands

```bash
# Projektstruktur anzeigen
python -m scripts.manage structure

# Datenbankstatus
python -m scripts.manage info

# Backup erstellen
python -m scripts.manage backup

# Verzeichnisse initialisieren
python -m scripts.manage init
```

## 📊 Datenformat

### invoices.json

```json
[
  {
    "id": "sha256(invoice_number + year)",
    "invoice_number": "SR25-00734",
    "invoice_date": "2025-08-01",
    "invoice_year": 2025,
    "invoice_month": 8,
    "vendor": "Lieferant Name",
    "gross_total": "1234.56",
    "net_total": "1000.00",
    "vat_total": "234.56",
    "currency": "EUR",
    "status": "SUCCESS",
    "line_items": []
  }
]
```

### line_items.json

```json
[
  {
    "id": "position_hash",
    "invoice_id": "...",
    "name": "Produktname",
    "quantity": 5,
    "unit_price": "100.00",
    "total_price": "500.00",
    "tax_rate": "19.0"
  }
]
```

## 🔄 Workflow: PDF vs XML

### PDF-Quelle
```
Rechnungen/2025/*.pdf
    ↓ (pdfplumber)
Text-Extraktion (manuell parsieren)```json
{
  "files_tracked": {
    "Rechnungen/2024/rechnung_001.pdf": {
      "hash": "abc123...",
      "mtime": 1702656000.0,
      "parser_version": "1.0.0"
    }
  },
  "last_scanned": "2025-01-27T10:30:45.123456",
  "parser_version": "1.0.0"
}
```

### errors.json

```json
[
  {
    "id": "err123...",
    "rel_path": "Rechnungen/2024/broken.pdf",
    "invoice_year": 2024,
    "file_hash": "xyz789...",
    "error_message": "Could not extract gross total (critical field)",
    "error_type": "parse_error",
    "timestamp": "2025-01-27T10:30:45.123456"
  }
]
```

## Web-Interface

### Übersichtsseite (`/`)

- **KPI-Karten:** Gesamtrechnungen, Gesamtbrutto, Fehleranzahl
- **Filter-Panel:** Nach Jahr, Lieferant (Auto-Refresh)
- **Rechnungstabelle:** Mit Datum, Lieferant, Nummer, Brutto, Status, Link zu Details
- **Top-Lieferanten:** Top 10 nach Bruttosumme
- **Nach Jahr:** Aggregierte Statistiken pro Jahr

### Detail-Seite (`/invoice/{id}`)

- Vollständige Metadaten (Datum, Nummer, Lieferant, Beträge)
- Positionen-Tabelle (falls extrahiert)
- Status & Parsing-Notizen
- Technische Infos (ID, File-Hash)

### Fehler-Seite (`/errors`)

- Listet alle Rechnungen mit Parsing-Fehlern
- Fehlertyp und -meldung
- Zeitpunkt der Erfassung

## Parsing-Logik

### Extrahierte Felder

Priorität #1:
- **Brutto-Gesamtsumme** – Wird immer benötigt, sonst Fehler

Zusätzlich (optional):
- Rechnungsdatum (DD.MM.YYYY, DD/MM/YYYY, ISO-Format)
- Rechnungsnummer (alphanumerisch)
- Lieferant/Absender (aus ersten Zeilen)
- Netto-Summe & MwSt
- Positionen (tabellarisch via pdfplumber)

### Heuristische Muster

```
Rechnungsdatum: "Rechnungsdatum: 15.12.2024"
Rechnungsnummer: "Rechnung Nr. INV-2024-001"
Lieferant: Erste relevante Textzeile
Gesamtbetrag: "Gesamtbetrag: 1234,56 EUR"
```

### Fehlerbehandlung

- **parse_error** – PDF konnte nicht gelesen oder Kritische Felder fehlen
- **UNSICHER_POSITIONEN** – Positionen nicht zuverlässig extrahiert
- **SUCCESS** – Erfolgreich geparst mit allen Positionen

## Normalisierung

Alle Beträge und Daten werden normalisiert:

| Feld | Format | Beispiel |
|------|--------|---------|
| Betrag | Decimal-String (2 Dezimalen) | `"1234.56"` |
| Datum | ISO (YYYY-MM-DD) | `"2024-12-15"` |
| Jahr | Integer | `2024` |

Unterstützte Dezimalformate:
- Europäisch: `1.234,56` → `1234.56`
- Englisch: `1,234.56` → `1234.56`
- Einfach: `42.50`, `42,50` → `42.50`
- Mit Symbol: `€ 100,00`, `$ 100.00` → `100.00`

## Unit-Tests

```bash
pytest tests/ -v
```

Tests für Normalisierungsfunktionen:
- `test_normalize.py::TestNormalizeDecimal` – Dezimalformate
- `test_normalize.py::TestNormalizeDate` – Datumsformate
- `test_normalize.py::TestExtractYearFromPath` – Pfad-Parsing

## Repo-Struktur

```
pdf-rechnung/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI App & Routes
│   ├── ingest.py               # CLI für PDF-Ingest
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── schema.py           # Datenmodelle
│   │   └── json_store.py       # JSON-Persistierung
│   ├── parsing/
│   │   ├── __init__.py
│   │   ├── extract.py          # PDF-Parsing
│   │   ├── normalize.py        # Daten-Normalisierung
│   │   └── vendors.py          # Vendor-spezifische Hints
│   ├── templates/
│   │   ├── base.html           # Layout-Template
│   │   ├── index.html          # Übersichtsseite
│   │   ├── detail.html         # Detail-Seite
│   │   └── errors.html         # Fehler-Seite
│   └── static/                 # CSS, JS (optional)
│
├── tests/
│   ├── __init__.py
│   └── test_normalize.py       # Unit-Tests
│
├── Rechnungen/
│   ├── 2022/
│   ├── 2023/
│   ├── 2024/
│   └── 2025/
│
├── data/                       # .gitignored – geniert bei Ingest
│   ├── invoices.json
│   ├── line_items.json
│   ├── index.json
│   └── errors.json
│
├── requirements.txt            # Python-Dependencies
├── .gitignore
└── README.md                   # Diese Datei
```

## Workflow-Beispiel

### 1. Neue PDFs hinzufügen

```bash
# Kopieren Sie neue PDFs in Rechnungen/{YYYY}/
cp /path/to/rechnung_2024_001.pdf Rechnungen/2024/

# Ingest starten
python -m app.ingest

# Ergebnis: invoices.json, line_items.json updated
```

### 2. PDF aktualisiert (Korrektur)

```bash
# Ersetzen Sie die PDF (Dateigröße/Inhalt ändert sich → neuer Hash)
# Ingest erkennt Änderung automatisch und re-parst

python -m app.ingest

# Neue Daten in JSON geschrieben
```

### 3. PDF löschen

```bash
# Entfernen Sie die PDF
rm Rechnungen/2024/rechnung_old.pdf

# Mit --prune räumen auf
python -m app.ingest --prune

# JSON-Einträge für gelöschte PDF entfernt
```

## Troubleshooting

### Problem: "Rechnungen directory not found"

Stellen Sie sicher, dass das `Rechnungen/` Verzeichnis im Root des Repos existiert.

```bash
mkdir -p Rechnungen/{2022,2023,2024,2025}
```

### Problem: "Could not extract gross total"

Die PDF konnte geparst werden, aber die Brutto-Summe konnte nicht extrahiert werden. Das ist ein kritischer Fehler, daher wird die Rechnung mit Fehler gespeichert.

**Lösung:** Überprüfen Sie das PDF manuell und möglicherweise müssen die Heuristiken in `parsing/extract.py` erweitert werden.

### Problem: "Positionen unsicher"

Die Positionen wurden nicht zuverlässig aus Tabellen extrahiert. Status: `UNSICHER_POSITIONEN`.

**Lösung:** Manuell überprüfen oder in der Detail-Seite zusätzliche Informationen hinzufügen.

### Problem: Web-UI zeigt keine Daten

1. Überprüfen Sie, dass Ingest gelaufen ist: `ls -la data/invoices.json`
2. Starten Sie die App neu: `uvicorn app.main:app --reload`
3. Öffnen Sie http://localhost:8000

## Performance & Skalierung

- **PDFs:** System aktuell getestet mit bis zu ~1000 PDFs
- **JSON-Dateien:** Komplett im RAM geladen bei jedem Request
- **Ingest:** ~100 PDFs pro Minute auf Standard-Hardware

Für größere Mengen (10.000+ PDFs):
- Optional: SQLite-Backend hinzufügen
- Optional: Redis-Cache für häufige Abfragen

## Lizenzen & Dependencies

Siehe `requirements.txt`:
- FastAPI (MIT)
- pdfplumber (MIT)
- pypdf (BSD)
- Jinja2 (BSD)
- python-dateutil (Dual: Apache 2.0 / BSD)
- pytest (MIT)

## Changelog

### v1.0.0 (2025-01-27)

- ✅ Initial Release
- ✅ PDF Scanning & Parsing
- ✅ JSON Persistierung
- ✅ Web-UI mit Filtern & KPIs
- ✅ Unit-Tests
- ✅ Dokumentation

## Roadmap

- [ ] OCR-Support für gescannte Rechnungen
- [ ] Duplicate Detection (ähnliche PDFs)
- [ ] Batch-Export (CSV, Excel)
- [ ] Multi-Currency-Support
- [ ] PDF-Viewer integriert (iframe)
- [ ] Dark Mode

## Support

Bei Fragen oder Problemen:

1. Überprüfen Sie das Troubleshooting
2. Schauen Sie sich die Logs an: `python -m app.ingest --debug`
3. Prüfen Sie die `errors.json` auf spezifische Parse-Fehler

---

**Erstellt für lokale, offline Rechnungsverwaltung ohne Cloud-Abhängigkeiten.**
