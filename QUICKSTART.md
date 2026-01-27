# QUICKSTART – PDF Rechnungen

Schneller Einstieg in 5 Minuten!

## 1. Installation

### Windows

```batch
cd "c:\Users\User\OneDrive\Desktop\Shop\Rechnungen Shop\pdf-rechnung"
install.bat
```

Das wird:
- ✓ Python venv erstellen
- ✓ Dependencies installieren
- ✓ Verzeichnisse anlegen

### macOS / Linux

```bash
cd "pdf-rechnung"
bash install.sh
```

## 2. PDFs vorbereiten

Kopieren Sie Ihre Rechnungs-PDFs in die richtige Ordnerstruktur:

```
Rechnungen/
├── 2022/
│   └── ihre_rechnung_001.pdf
├── 2023/
│   └── ihre_rechnung_002.pdf
├── 2024/
│   └── ihre_rechnung_003.pdf
└── 2025/
    └── ihre_rechnung_004.pdf
```

**Wichtig:** Der Ordnername `{YYYY}` wird als Rechnungsjahr verwendet!

## 3. Ingest durchführen

```bash
# Virtual Environment aktivieren (falls noch nicht aktiv)
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# PDFs scannen und verarbeiten
python -m app.ingest
```

**Ergebnis:** PDFs werden analysiert und Daten in `./data/` gespeichert.

Console-Ausgabe beispiel:
```
INFO:__main__:Scanning PDFs in ...
INFO:__main__:Found 50 PDF(s)
INFO:__main__:Parsing: Rechnungen/2024/rechnung_001.pdf
INFO:__main__:Parsing: Rechnungen/2025/rechnung_002.pdf
...
==================================================
Ingest Summary:
  Total PDFs: 50
  Parsed: 48
  Updated: 0
  Skipped: 0
  Errors: 2
==================================================
```

## 4. Web-UI starten

```bash
uvicorn app.main:app --reload
```

Output:
```
Uvicorn running on http://127.0.0.1:8000
```

## 5. Browser öffnen

Navigieren Sie zu: **http://localhost:8000**

Sie sollten sehen:
- 📊 KPI-Übersicht (Anzahl, Gesamtbrutto, Fehler)
- 📋 Rechnungstabelle mit Filtern
- 💰 Top-Lieferanten
- 📈 Jahresstatistiken

---

## Häufige Befehle

```bash
# PDFs re-parsen (Cache ignorieren)
python -m app.ingest --force

# Gelöschte PDFs aus JSON entfernen
python -m app.ingest --prune

# Beides kombiniert
python -m app.ingest --force --prune

# Ausführliches Logging
python -m app.ingest --debug

# Unit-Tests durchführen
pytest tests/ -v

# Entwicklungsserver starten
uvicorn app.main:app --reload

# Produktionsserver (ohne reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Troubleshooting

### 1. "Python not found"

→ Python nicht installiert. Download: https://www.python.org/

**Windows:** Während Installation "Add Python to PATH" ankreuzen!

### 2. "No module named 'pdfplumber'"

→ Dependencies nicht installiert.

```bash
pip install -r requirements.txt
```

### 3. "Rechnungen directory not found"

→ Ordnerstruktur wird vom Ingest erstellt:

```bash
python -m app.ingest
```

Falls manuell:
```bash
mkdir -p Rechnungen/{2022,2023,2024,2025}
```

### 4. Web-UI lädt aber zeigt keine Daten

→ Ingest noch nicht durchgeführt oder fehlgeschlagen.

Überprüfen Sie:
```bash
ls -la data/invoices.json  # macOS/Linux
dir data\invoices.json      # Windows
```

Falls nicht vorhanden → Ingest durchführen:
```bash
python -m app.ingest --debug
```

### 5. PDFs werden nicht gefunden

→ Falsche Ordnerstruktur. Überprüfen Sie:
- PDF liegt in `Rechnungen/2024/` (oder passendem Jahr)?
- Ordner existiert wirklich? `ls -R Rechnungen/`

---

## Workflow: Neue Rechnungen hinzufügen

1. **PDF kopieren** in `Rechnungen/{YYYY}/`
   ```bash
   cp ~/Downloads/rechnung_xyz.pdf ./Rechnungen/2024/
   ```

2. **Ingest starten**
   ```bash
   python -m app.ingest
   ```

3. **Web-UI aktualisieren** (Browser F5 oder Ctrl+R)
   - Die neue Rechnung sollte in der Tabelle erscheinen

4. **Optional: Details anschauen**
   - Click auf Rechnung → Detail-Seite öffnet sich

---

## Nächste Schritte

Nach dem erfolgreichen Start:

1. **Parsing verbessern** (falls Fehler)
   - Schaue auf Fehler-Seite: `/errors`
   - Edit `app/parsing/extract.py` für bessere Heuristiken

2. **Filter & KPIs verwenden**
   - Jahr filtern
   - Lieferant filtern
   - Top-Lieferanten analysieren

3. **Daten exportieren** (Feature kommt)
   - Momentan als JSON verfügbar in `./data/invoices.json`

4. **Optional: In Git committen**
   ```bash
   git add app/ requirements.txt README.md Makefile
   git commit -m "Add PDF invoice management system"
   git push
   ```

---

## Support & Debugging

**Verbose Output beim Ingest:**
```bash
python -m app.ingest --debug
```

**Fehler ansehen:**
- Öffne http://localhost:8000/errors
- Oder schaue in `./data/errors.json`

**Einzelne PDF testen:**
```python
# Interaktiv in Python
from app.parsing import parse_invoice
from pathlib import Path

pdf = Path("Rechnungen/2024/test.pdf")
invoice, error = parse_invoice(pdf, "Rechnungen/2024/test.pdf")
if error:
    print(f"Error: {error}")
else:
    print(f"Invoice: {invoice.invoice_number} - {invoice.gross_total}")
```

---

Viel Erfolg! 🚀
