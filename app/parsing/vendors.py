"""
Vendor-specific extraction hints (optional).
"""

# Vendor-specific patterns for common invoice structures
VENDOR_PATTERNS = {
    # Example: if you know certain vendors always have gross total in specific positions
    # This could help heuristics later
}


def get_vendor_hint(vendor_name: str) -> dict:
    """
    Get extraction hints for a specific vendor.
    Returns empty dict if no specific hints.
    """
    if not vendor_name:
        return {}
    
    vendor_lower = vendor_name.lower()
    return VENDOR_PATTERNS.get(vendor_lower, {})
