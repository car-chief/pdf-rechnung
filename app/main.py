"""
FastAPI application for invoice management and viewing.
"""
from fastapi import FastAPI, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Optional
from datetime import datetime
from decimal import Decimal

from .storage import JSONStore, ParsingStatus

# Initialize FastAPI app
app = FastAPI(title="PDF Rechnungen", description="Invoice overview and management")

# Setup paths
APP_DIR = Path(__file__).parent
TEMPLATE_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"
DATA_DIR = Path(__file__).parent.parent / "data"

# Setup Jinja2
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)

# Setup static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Initialize storage
store = JSONStore(str(DATA_DIR))


# ============================================================================
# Utility Functions
# ============================================================================

def get_all_years() -> list:
    """Get sorted list of all unique years from invoices."""
    invoices = store.load_invoices()
    years = sorted(set(inv.invoice_year for inv in invoices if inv.invoice_year))
    return years


def get_all_vendors() -> list:
    """Get sorted list of all unique vendors."""
    invoices = store.load_invoices()
    vendors = sorted(set(inv.vendor for inv in invoices if inv.vendor))
    return vendors


def calculate_kpis():
    """Calculate KPIs for the dashboard."""
    invoices = store.load_invoices()
    
    kpis = {
        "total_gross": Decimal("0"),
        "total_net": Decimal("0"),
        "total_count": len(invoices),
        "by_year": {},
        "top_vendors": {},
        "error_count": 0,
    }
    
    # Calculate by year and vendor
    for inv in invoices:
        if inv.invoice_year:
            if inv.invoice_year not in kpis["by_year"]:
                kpis["by_year"][inv.invoice_year] = {
                    "gross": Decimal("0"),
                    "net": Decimal("0"),
                    "count": 0,
                }
            
            year_data = kpis["by_year"][inv.invoice_year]
            year_data["count"] += 1
            
            if inv.gross_total:
                gross = Decimal(inv.gross_total)
                year_data["gross"] += gross
                kpis["total_gross"] += gross
            
            if inv.net_total:
                net = Decimal(inv.net_total)
                year_data["net"] += net
                kpis["total_net"] += net
        
        # Top vendors
        if inv.vendor:
            if inv.vendor not in kpis["top_vendors"]:
                kpis["top_vendors"][inv.vendor] = {
                    "count": 0,
                    "gross": Decimal("0"),
                }
            
            vendor_data = kpis["top_vendors"][inv.vendor]
            vendor_data["count"] += 1
            if inv.gross_total:
                vendor_data["gross"] += Decimal(inv.gross_total)
    
    # Sort top vendors by gross total
    kpis["top_vendors"] = dict(
        sorted(
            kpis["top_vendors"].items(),
            key=lambda x: x[1]["gross"],
            reverse=True
        )[:10]  # Top 10
    )
    
    # Count errors
    errors = store.load_errors()
    kpis["error_count"] = len(errors)
    
    return kpis


def format_decimal(value: str) -> str:
    """Format decimal string for display."""
    if not value:
        return "-"
    try:
        d = Decimal(value)
        return f"€ {d:,.2f}".replace(",", " ").replace(".", ",")
    except:
        return value


# Register Jinja2 filters
jinja_env.filters['format_decimal'] = format_decimal


# ============================================================================
# Routes
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    year: Optional[int] = Query(None),
    vendor: Optional[str] = Query(None),
):
    """
    Invoice index page with filtering.
    """
    invoices = store.load_invoices()
    
    # Filter by year
    if year:
        invoices = [inv for inv in invoices if inv.invoice_year == year]
    
    # Filter by vendor
    if vendor:
        invoices = [inv for inv in invoices if inv.vendor == vendor]
    
    # Sort by date desc, then by invoice number
    invoices = sorted(
        invoices,
        key=lambda x: (x.invoice_date or "0000-00-00", x.invoice_number or ""),
        reverse=True
    )
    
    # Prepare context
    context = {
        "invoices": invoices,
        "all_years": get_all_years(),
        "all_vendors": get_all_vendors(),
        "selected_year": year,
        "selected_vendor": vendor,
        "invoice_count": len(invoices),
        "kpis": calculate_kpis(),
    }
    
    template = jinja_env.get_template("index.html")
    return template.render(context)


@app.get("/invoice/{invoice_id}", response_class=HTMLResponse)
async def detail(invoice_id: str):
    """
    Invoice detail page.
    """
    invoices = store.load_invoices()
    invoice = next((inv for inv in invoices if inv.id == invoice_id), None)
    
    if not invoice:
        return "<h1>Invoice not found</h1>", 404
    
    # Load line items
    line_items = store.load_line_items()
    invoice_items = [item for item in line_items if item.invoice_id == invoice_id]
    
    context = {
        "invoice": invoice,
        "line_items": invoice_items,
    }
    
    template = jinja_env.get_template("detail.html")
    return template.render(context)


@app.get("/errors", response_class=HTMLResponse)
async def errors_page():
    """
    Show parsing errors.
    """
    errors = store.load_errors()
    errors = sorted(errors, key=lambda x: x.timestamp, reverse=True)
    
    context = {
        "errors": errors,
        "error_count": len(errors),
    }
    
    template = jinja_env.get_template("errors.html")
    return template.render(context)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
