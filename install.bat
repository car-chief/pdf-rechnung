@echo off
REM Installation script for PDF Rechnungen (Windows)

setlocal enabledelayedexpansion

echo ======================================
echo PDF Rechnungen - Installation (Windows)
echo ======================================
echo.

REM Check Python version
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python not found! Please install Python 3.11+
    echo   Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Found Python %PYTHON_VERSION%
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ℹ Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
echo ✓ Dependencies installed
echo.

REM Create directories
echo Creating directory structure...
if not exist "data" mkdir data
if not exist "Rechnungen\2022" mkdir Rechnungen\2022
if not exist "Rechnungen\2023" mkdir Rechnungen\2023
if not exist "Rechnungen\2024" mkdir Rechnungen\2024
if not exist "Rechnungen\2025" mkdir Rechnungen\2025
echo ✓ Directories created
echo.

echo ======================================
echo Installation Complete!
echo ======================================
echo.
echo Next steps:
echo   1. Copy PDFs into Rechnungen/{YYYY}/ folders
echo.
echo   2. Activate virtual environment:
echo      venv\Scripts\activate.bat
echo.
echo   3. Scan PDF files:
echo      python -m app.ingest
echo.
echo   4. Start the web server:
echo      uvicorn app.main:app --reload
echo.
echo   5. Open in browser:
echo      http://localhost:8000
echo.
pause
