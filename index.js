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

  const fallback = text.match(/rechnung[^\n]{0,30}([A-Z0-9\-\/\.]{3,})/i);
  if (fallback && fallback[1]) return fallback[1].trim();

  return null;
}

function shortenFilename(filename) {
  const ext = path.extname(filename);
  const base = path.basename(filename, ext);
  if (base.length <= 12) return filename;
  return base.slice(0, 8) + "..." + base.slice(-4) + ext;
}

async function parseFolder(folderName, folderPath) {
  const invoices = [];
  let folderTotal = 0;
  const files = fs.readdirSync(folderPath);
  for (const file of files) {
    const filePath = path.join(folderPath, file);
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
      folderTotal += amount;
      invoices.push({ file, invoice: invoiceNumber, amount });
      console.log(
        `[${folderName}]`,
        shortenFilename(file),
        "=>",
        amount,
        invoiceNumber ? `(${invoiceNumber})` : "(keine Rechnungsnummer)"
      );
    } catch (err) {
      console.warn("Fehler beim Verarbeiten von", file, err.message);
    }
  }
  return { total: Number(folderTotal.toFixed(2)), invoices };
}

async function main() {
  if (!fs.existsSync(billsDir) || !fs.statSync(billsDir).isDirectory()) {
    console.error("src-Ordner nicht gefunden:", billsDir);
    process.exit(1);
  }

  const folders = fs.readdirSync(billsDir).filter((f) => {
    const p = path.join(billsDir, f);
    return fs.statSync(p).isDirectory();
  });

  const outputInvoices = {};
  let grandTotal = 0;
  for (const folder of folders) {
    const folderPath = path.join(billsDir, folder);
    const result = await parseFolder(folder, folderPath);
    outputInvoices[folder] = result; // result enthält jetzt total und invoices
    grandTotal += result.total;
    console.log(`[${folder}] Total: ${result.total.toFixed(2)} EUR`);
    console.log("------------------------------");
  }

  const output = {
    total: Number(grandTotal.toFixed(2)),
    invoices: outputInvoices,
  };

  const outDir = path.join(__dirname, "dist");
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

  fs.writeFileSync(
    path.join(outDir, "invoices.json"),
    JSON.stringify(output, null, 2)
  );
  console.log("Gespeichert:", path.join(outDir, "invoices.json"));
  console.log("------------------------------");
  console.log("Gesamtsumme:", output.total.toFixed(2), "EUR");
  console.log("==============================");
}

main();
