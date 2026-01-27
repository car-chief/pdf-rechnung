#!/usr/bin/env python3
"""
Quick analysis script for invoice data
"""
import json
from pathlib import Path
from decimal import Decimal

data_dir = Path("data")

print("\n" + "="*60)
print("  📊 RECHNUNGS-AUSWERTUNG")
print("="*60 + "\n")

try:
    # Load invoices
    with open(data_dir / "invoices.json") as f:
        invoices = json.load(f)
    
    if not invoices:
        print("❌ Keine Rechnungen gefunden! Bitte zuerst Ingest durchführen.")
        print("   python -m app.ingest\n")
        exit(1)
    
    # Calculations
    total_gross = Decimal("0")
    total_net = Decimal("0")
    by_year = {}
    by_vendor = {}
    error_count = 0
    
    for inv in invoices:
        # Sum
        if inv.get("gross_total"):
            gross = Decimal(inv["gross_total"])
            total_gross += gross
        
        if inv.get("net_total"):
            net = Decimal(inv["net_total"])
            total_net += net
        
        # By Year
        year = inv.get("invoice_year")
        if year:
            if year not in by_year:
                by_year[year] = {"count": 0, "gross": Decimal("0"), "net": Decimal("0")}
            by_year[year]["count"] += 1
            if inv.get("gross_total"):
                by_year[year]["gross"] += Decimal(inv["gross_total"])
            if inv.get("net_total"):
                by_year[year]["net"] += Decimal(inv["net_total"])
        
        # By Vendor
        vendor = inv.get("vendor", "Unbekannt")
        if vendor not in by_vendor:
            by_vendor[vendor] = {"count": 0, "gross": Decimal("0")}
        by_vendor[vendor]["count"] += 1
        if inv.get("gross_total"):
            by_vendor[vendor]["gross"] += Decimal(inv["gross_total"])
        
        # Errors
        if inv.get("status") == "ERROR":
            error_count += 1
    
    # Print Summary
    print(f"📈 GESAMTUMSATZ")
    print(f"   Rechnungen:     {len(invoices):>8}")
    print(f"   Brutto-Summe:   € {total_gross:>14,.2f}".replace(",", " ").replace(".", ","))
    print(f"   Netto-Summe:    € {total_net:>14,.2f}".replace(",", " ").replace(".", ","))
    
    if error_count > 0:
        print(f"   ⚠️  Fehler:       {error_count:>8}")
    print()
    
    # By Year
    if by_year:
        print(f"📅 NACH JAHR")
        for year in sorted(by_year.keys(), reverse=True):
            data = by_year[year]
            print(f"   {year}: {data['count']:>3} Rechnungen | "
                  f"€ {data['gross']:>10,.2f}".replace(",", " ").replace(".", ","))
        print()
    
    # Top Vendors
    if by_vendor:
        print(f"🏢 TOP LIEFERANTEN")
        sorted_vendors = sorted(by_vendor.items(), key=lambda x: x[1]["gross"], reverse=True)[:5]
        for vendor, data in sorted_vendors:
            vendor_short = (vendor[:25] + "...") if len(vendor) > 25 else vendor
            print(f"   {vendor_short:<28} | {data['count']:>2} Rechnungen | "
                  f"€ {data['gross']:>10,.2f}".replace(",", " ").replace(".", ","))
        print()
    
    print("="*60)
    print(f"✅ System bereit! Web-UI wird gestartet...")
    print("="*60 + "\n")

except FileNotFoundError:
    print("❌ Fehler: data/invoices.json nicht gefunden!")
    print("   Bitte führen Sie zuerst den Ingest durch:")
    print("   python -m app.ingest\n")
    exit(1)
except Exception as e:
    print(f"❌ Fehler: {e}\n")
    exit(1)
