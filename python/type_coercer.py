"""
Type coercion and validation for tender records
Standardizes data types and validates required fields
"""

from datetime import datetime
from typing import Dict, Any
import re


def coerce_types(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Coerce and validate data types in tender record.
    
    Args:
        record: Raw tender data dictionary
        
    Returns:
        Record with coerced types and validation flags
    """
    coerced = record.copy()
    
    # Convert resource_id to integer
    try:
        if coerced.get('resource_id'):
            coerced['resource_id'] = int(coerced['resource_id'])
    except (ValueError, TypeError):
        coerced['resource_id'] = None
    
    # Parse dates
    coerced['date_published_parsed'] = parse_date(coerced.get('date_published', ''))
    coerced['submission_deadline_parsed'] = parse_date(coerced.get('submission_deadline', ''))
    coerced['award_date_parsed'] = parse_date(coerced.get('award_date', ''))
    
    # Convert estimated_value to float
    try:
        value_str = coerced.get('estimated_value', '')
        if value_str:
            # Remove commas and convert to float
            value_clean = re.sub(r'[,\s]', '', str(value_str))
            coerced['estimated_value_numeric'] = float(value_clean)
        else:
            coerced['estimated_value_numeric'] = None
    except (ValueError, TypeError):
        coerced['estimated_value_numeric'] = None
    
    # Convert cycle to integer
    try:
        if coerced.get('cycle'):
            coerced['cycle_numeric'] = int(coerced['cycle'])
        else:
            coerced['cycle_numeric'] = None
    except (ValueError, TypeError):
        coerced['cycle_numeric'] = None
    
    # Add validation flags
    coerced['has_pdf_url'] = bool(coerced.get('notice_pdf_url'))
    coerced['has_estimated_value'] = coerced['estimated_value_numeric'] is not None
    coerced['is_open'] = coerced.get('status', '').lower() == 'open'
    
    return coerced


def parse_date(date_str: str) -> str:
    """
    Parse date string to ISO format.
    
    Args:
        date_str: Date string from eTenders (e.g., "Mon Nov 17 16:51:52 GMT 2025")
        
    Returns:
        ISO formatted date string or empty string if parsing fails
    """
    if not date_str:
        return ''
    
    try:
        # Try parsing the eTenders format
        # Example: "Mon Nov 17 16:51:52 GMT 2025"
        formats = [
            '%a %b %d %H:%M:%S %Z %Y',  # Mon Nov 17 16:51:52 GMT 2025
            '%a %b %d %H:%M:%S %Z %Y',  # Mon Nov 17 16:51:52 IST 2025
            '%d/%m/%Y %H:%M',           # 01/07/2025 12:00
            '%d/%m/%Y',                 # 01/07/2025
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.isoformat()
            except ValueError:
                continue
        
        # If no format matched, return original
        return date_str
        
    except Exception:
        return date_str


if __name__ == "__main__":
    # Test type coercion
    test_record = {
        'row_number': '5',
        'title': 'Test Tender',
        'resource_id': '6972976',
        'date_published': 'Mon Nov 17 16:51:52 GMT 2025',
        'submission_deadline': 'Fri Dec 31 23:45:00 GMT 2027',
        'estimated_value': '1,500,000',
        'cycle': '1',
        'status': 'Open',
        'notice_pdf_url': 'https://example.com/notice.pdf'
    }
    
    coerced = coerce_types(test_record)
    
    print("Original record:")
    print(test_record)
    print("\nCoerced record:")
    for key, value in coerced.items():
        if key not in test_record or test_record.get(key) != value:
            print(f"  {key}: {value}")
