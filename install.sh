#!/bin/bash
# Installation script for PDF Rechnungen

set -e

echo "======================================"
echo "PDF Rechnungen - Installation"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python installation..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "ℹ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create directories
echo "Creating directory structure..."
mkdir -p data
mkdir -p Rechnungen/{2022,2023,2024,2025}
echo "✓ Directories created"
echo ""

echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Scan PDF files:"
echo "     python -m app.ingest"
echo ""
echo "  3. Start the web server:"
echo "     uvicorn app.main:app --reload"
echo ""
echo "  4. Open in browser:"
echo "     http://localhost:8000"
echo ""
