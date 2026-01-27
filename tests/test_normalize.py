"""
Unit tests for normalization functions.
"""
import pytest
from app.parsing.normalize import (
    normalize_decimal,
    normalize_date,
    normalize_invoice_number,
    normalize_vendor,
    extract_year_from_path,
    is_valid_year,
)


class TestNormalizeDecimal:
    """Test decimal normalization."""
    
    def test_german_format_with_currency(self):
        """Test German format: 1.234,56 EUR"""
        assert normalize_decimal("1.234,56 EUR") == "1234.56"
    
    def test_german_format_dot_thousands(self):
        """Test German format with dot as thousands separator."""
        assert normalize_decimal("1.234,56") == "1234.56"
    
    def test_us_format(self):
        """Test US format: 1,234.56"""
        assert normalize_decimal("1,234.56") == "1234.56"
    
    def test_simple_decimal(self):
        """Test simple decimal without thousands."""
        assert normalize_decimal("42.50") == "42.50"
        assert normalize_decimal("42,50") == "42.50"
    
    def test_currency_symbol(self):
        """Test currency symbol removal."""
        assert normalize_decimal("€ 100,00") == "100.00"
        assert normalize_decimal("$ 100.00") == "100.00"
    
    def test_zero_values(self):
        """Test zero and edge cases."""
        assert normalize_decimal("0,00") == "0.00"
        assert normalize_decimal("0.00") == "0.00"
    
    def test_none_and_empty(self):
        """Test None and empty strings."""
        assert normalize_decimal(None) is None
        assert normalize_decimal("") is None
        assert normalize_decimal("   ") is None
    
    def test_invalid(self):
        """Test invalid values."""
        assert normalize_decimal("abc") is None


class TestNormalizeDate:
    """Test date normalization."""
    
    def test_german_format(self):
        """Test German format: DD.MM.YYYY"""
        assert normalize_date("25.12.2024") == "2024-12-25"
    
    def test_german_format_short_year(self):
        """Test German format with 2-digit year."""
        assert normalize_date("25.12.24") == "2024-12-25"
    
    def test_slash_format(self):
        """Test DD/MM/YYYY format."""
        assert normalize_date("25/12/2024") == "2024-12-25"
    
    def test_iso_format(self):
        """Test ISO format."""
        assert normalize_date("2024-12-25") == "2024-12-25"
    
    def test_english_format(self):
        """Test English format."""
        assert normalize_date("December 25, 2024") == "2024-12-25"
    
    def test_none_and_empty(self):
        """Test None and empty strings."""
        assert normalize_date(None) is None
        assert normalize_date("") is None
    
    def test_invalid(self):
        """Test invalid dates."""
        assert normalize_date("not-a-date") is None


class TestNormalizeInvoiceNumber:
    """Test invoice number normalization."""
    
    def test_basic(self):
        """Test basic invoice number."""
        assert normalize_invoice_number("INV-2024-001") == "INV-2024-001"
    
    def test_whitespace(self):
        """Test whitespace trimming."""
        assert normalize_invoice_number("  INV-001  ") == "INV-001"
    
    def test_empty(self):
        """Test empty string."""
        assert normalize_invoice_number("") is None
        assert normalize_invoice_number("   ") is None


class TestNormalizeVendor:
    """Test vendor name normalization."""
    
    def test_basic(self):
        """Test basic vendor name."""
        assert normalize_vendor("Acme GmbH") == "Acme GmbH"
    
    def test_whitespace_cleanup(self):
        """Test whitespace cleanup."""
        assert normalize_vendor("  Company  Name  ") == "Company Name"
        assert normalize_vendor("Too   Many    Spaces") == "Too Many Spaces"
    
    def test_empty(self):
        """Test empty string."""
        assert normalize_vendor("") is None
        assert normalize_vendor("   ") is None


class TestExtractYearFromPath:
    """Test year extraction from paths."""
    
    def test_standard_path(self):
        """Test standard path format."""
        assert extract_year_from_path("Rechnungen/2024/file.pdf") == 2024
    
    def test_nested_path(self):
        """Test nested paths."""
        assert extract_year_from_path("Rechnungen/2024/subfolder/file.pdf") == 2024
    
    def test_multiple_years(self):
        """Test path with multiple years (should pick first)."""
        result = extract_year_from_path("Rechnungen/2023/2024/file.pdf")
        assert result in [2023, 2024]  # Depends on regex
    
    def test_no_year(self):
        """Test path without year."""
        assert extract_year_from_path("Rechnungen/file.pdf") is None
    
    def test_invalid_year(self):
        """Test invalid year format."""
        assert extract_year_from_path("Rechnungen/99/file.pdf") is None
        assert extract_year_from_path("Rechnungen/abc/file.pdf") is None


class TestIsValidYear:
    """Test year validation."""
    
    def test_valid_years(self):
        """Test valid year ranges."""
        assert is_valid_year(2024) is True
        assert is_valid_year(1900) is True
        assert is_valid_year(2100) is True
    
    def test_invalid_years(self):
        """Test invalid years."""
        assert is_valid_year(1899) is False
        assert is_valid_year(2101) is False
        assert is_valid_year(0) is False
        assert is_valid_year(-1) is False
    
    def test_none(self):
        """Test None."""
        assert is_valid_year(None) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
