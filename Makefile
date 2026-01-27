.PHONY: install dev test ingest ingest-force ingest-prune clean help

help:
	@echo "PDF Rechnungen - Available Commands:"
	@echo ""
	@echo "  make install       - Install dependencies"
	@echo "  make dev           - Install dependencies in development mode"
	@echo "  make ingest        - Run PDF ingest"
	@echo "  make ingest-force  - Re-parse all PDFs"
	@echo "  make ingest-prune  - Ingest + remove deleted PDFs"
	@echo "  make serve         - Start development server"
	@echo "  make test          - Run unit tests"
	@echo "  make clean         - Remove __pycache__ and .pytest_cache"
	@echo ""

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt
	pip install -e .

ingest:
	python -m app.ingest

ingest-force:
	python -m app.ingest --force

ingest-prune:
	python -m app.ingest --prune --force

serve:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete

all: install ingest serve
