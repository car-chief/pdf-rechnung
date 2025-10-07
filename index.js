const fs = require("fs");
const path = require("path");
const pdfParse = require("pdf-parse");

const billsDir = path.join(__dirname, "src");
let totalAmount = 0;

function extractInvoiceNumber(text) {
  if (!text) return null;
  const regexes = [
    /rechnungsnummer[:\s]*([A-Z0-9\-\/\.]+)/i,
    /rechnungsnr\.?[:\s]*([A-Z0-9\-\/\.]+)/i,
    /rechnung\s*nr\.?[:\s]*([A-Z0-9\-\/\.]+)/i,
    /rechnung[:\s]*#?([A-Z0-9\-\/\.]{3,})/i,
    /invoice(?:\s*no\.?|number|#)?[:\s]*([A-Z0-9\-\/\.]+)/i,
    /\binv[:\s]*([A-Z0-9\-\/\.]+)/i,
  ];

  for (const r of regexes) {
    const m = text.match(r);
    if (m && m[1]) return m[1].trim();
  }

  // Fallback: look for "Rechnung" followed by a nearby token that looks like an id
  const fallback = text.match(/rechnung[^\n]{0,30}([A-Z0-9\-\/\.]{3,})/i);
  if (fallback && fallback[1]) return fallback[1].trim();

  return null;
}

/**
 * Hauptfunktion zum Parsen von PDF-Rechnungen aus einem Verzeichnis.
 *
 * - Überprüft, ob das Rechnungs-Verzeichnis existiert und gültig ist.
 * - Liest alle PDF-Dateien im Verzeichnis aus.
 * - Extrahiert den Rechnungsbetrag und die Rechnungsnummer aus jeder Datei.
 * - Summiert alle gefundenen Beträge.
 * - Speichert die Ergebnisse als JSON-Datei im "dist"-Ordner.
 * - Gibt Status- und Fehlermeldungen auf der Konsole aus.
 *
 * @async
 * @function
 * @returns {Promise<void>} Gibt ein Promise zurück, das abgeschlossen wird, wenn alle Rechnungen verarbeitet wurden.
 */
async function main() {
  if (!fs.existsSync(billsDir) || !fs.statSync(billsDir).isDirectory()) {
    console.error("src-Ordner nicht gefunden:", billsDir);
    process.exit(1);
  }

  const files = fs.readdirSync(billsDir);
  const invoices = [];

  for (const file of files) {
    const filePath = path.join(billsDir, file);
    if (!fs.statSync(filePath).isFile()) continue;
    if (!file.toLowerCase().endsWith(".pdf")) continue;

    try {
      const dataBuffer = fs.readFileSync(filePath);
      const data = await pdfParse(dataBuffer);

      const match =
        data.text.match(
          /(?:amount|total|betrag|gesamtpreis)[:\s]*([€$]?\s*[\d\.,]+)/i
        ) || data.text.match(/([€$]?\s*[\d\.,]+)\s*(?:€|eur)\b/i);

      if (!match) {
        console.warn("Kein Betrag gefunden in:", file);
        continue;
      }

      let raw = match[1].replace(/\s+/g, "");
      raw = raw.replace(/,/g, ".").replace(/[^0-9.-]/g, "");
      const amount = Number(raw);
      if (!Number.isFinite(amount)) {
        console.warn("Ungültiger Betrag in:", file, "->", match[1]);
        continue;
      }

      const invoiceNumber = extractInvoiceNumber(data.text);
      totalAmount += amount;
      invoices.push({ file, invoice: invoiceNumber, amount });
      console.log(
        "Geparst:",
        file,
        "=>",
        amount,
        invoiceNumber ? `(${invoiceNumber})` : "(keine Rechnungsnummer)"
      );
    } catch (err) {
      console.warn("Fehler beim Verarbeiten von", file, err.message);
    }
  }

  const output = {
    total: Number(totalAmount.toFixed(2)),
    invoices,
  };

  const outDir = path.join(__dirname, "dist");
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

  fs.writeFileSync(
    path.join(outDir, "invoices.json"),
    JSON.stringify(output, null, 2)
  );
  console.log("Gespeichert:", path.join(outDir, "invoices.json"));
  console.log("Total amount of all bills:", output.total.toFixed(2));
}

main();
