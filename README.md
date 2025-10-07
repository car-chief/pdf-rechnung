# pdf-rechnung

Dieses Projekt parst PDF‑Rechnungen und extrahiert Beträge sowie Rechnungsnummern. Die Ergebnisse werden als einzelne JSON‑Datei im Ordner `dist` gespeichert.

## Projektstruktur

- `index.js` – Hauptskript: liest PDF‑Dateien aus `src`, extrahiert Betrag und Rechnungsnummer und schreibt `dist/invoices.json`.
- `src` – Ordner für die PDF‑Rechnungen (einfach die PDF‑Dateien hier ablegen).
- `dist` – Wird bei Bedarf erstellt; enthält `invoices.json`.
- `package.json` – (optional) npm‑Konfiguration und Skripte.
- `README.md` – Diese Datei.

## Verwendung

1. PDFs in den Ordner `src` legen.
2. Abhängigkeit installieren (im Projektordner):
   ```
   npm install
   ```
3. Skript ausführen:

   ```
   npm start
   ```

   (Falls ein `package.json` mit einem `start`‑Script vorhanden ist, alternativ `npm start`.)

4. Ergebnis:
   - Datei: `dist/invoices.json`
   - Enthält die Gesamtsumme und ein Array `invoices` mit Einträgen:
     - `file`: Dateiname der PDF
     - `invoice`: erkannte Rechnungsnummer (falls vorhanden)
     - `amount`: Betrag als Zahl

## Hinweise

- Das Skript erstellt `dist`, falls der Ordner fehlt.
- Beträge werden flexibel erkannt (Punkt/Komma als Dezimaltrennzeichen, Währungssymbole werden entfernt).
- Rechnungsnummern werden heuristisch per regulären Ausdrücken extrahiert; bei Bedarf Regex anpassen, falls spezifische Formate nicht erkannt werden.
- Bei Problemen: Ausgabe in der Konsole prüfen, insbesondere Warnungen zu nicht gefundenen Beträgen oder Fehlern beim Parsen.

## Voraussetzungen

- Node.js (macOS: z. B. mit Homebrew: `brew install node`)

## Lizenz

MIT
