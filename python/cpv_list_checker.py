"""
CPV Code Checker - Extracts and validates CPV codes from tender records
Uses cpv_list.json to validate codes against known IT/software CPV codes
"""

import logging
import json
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


# Load CPV list once at module level
with open('cpv_list.json', 'r', encoding='utf-8') as f:
    CPV_LIST = json.load(f)
    CPV_CODES = {item['code']: item['description'] for item in CPV_LIST}


def extract_cpv_codes(record: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extract CPV codes from record (from PDF data or description).
    
    Args:
        record: Tender record with potential CPV codes
        
    Returns:
        List of CPV code dictionaries with code, description, and source
    """
    found_cpvs = []
    resource_id = record.get('resource_id', 'unknown')
    logger.debug(f"Extracting CPV codes for tender {resource_id}")
    
    # Check PDF data for main_classification
    pdf_data = record.get('pdf_data')
    if pdf_data and isinstance(pdf_data, dict):
        # Check structured main_classification field
        main_class = pdf_data.get('main_classification', '')
        if main_class:
            # Extract ALL CPV codes from main_classification (not just first)
            matches = re.findall(r'\b(\d{8})\b', main_class)
            for code in matches:
                if not any(cpv['code'] == code for cpv in found_cpvs):
                    found_cpvs.append({
                        'code': code,
                        'description': main_class,
                        'source': 'pdf_main_classification',
                        'validated': code in CPV_CODES
                    })
        
        # Also check pdf_content (organized sections) if it exists
        pdf_content = pdf_data.get('pdf_content', {})
        if isinstance(pdf_content, dict):
            for section_name, section_text in pdf_content.items():
                if isinstance(section_text, str):
                    matches = re.findall(r'\b(\d{8})\b', section_text)
                    for code in matches:
                        if code in CPV_CODES and not any(cpv['code'] == code for cpv in found_cpvs):
                            found_cpvs.append({
                                'code': code,
                                'description': CPV_CODES[code],
                                'source': f'pdf_content_{section_name}',
                                'validated': True
                            })
                            logger.debug(f"Found CPV code {code} in PDF section '{section_name}' for tender {resource_id}")
        
        # Check pdf_content_full_text if it exists (fallback when parsing fails)
        full_text = pdf_data.get('pdf_content_full_text', '')
        if full_text:
            matches = re.findall(r'\b(\d{8})\b', full_text)
            for code in matches:
                if code in CPV_CODES and not any(cpv['code'] == code for cpv in found_cpvs):
                    found_cpvs.append({
                        'code': code,
                        'description': CPV_CODES[code],
                        'source': 'pdf_full_text',
                        'validated': True
                    })
                    logger.debug(f"Found CPV code {code} in PDF full text for tender {resource_id}")
    
    # Search in title and info fields for CPV patterns
    searchable_text = ' '.join([
        str(record.get('title', '')),
        str(record.get('info', '')),
        str(record.get('contracting_authority', ''))
    ])
    
    # Find all 8-digit numbers that might be CPV codes
    potential_codes = re.findall(r'\b(\d{8})\b', searchable_text)
    
    for code in potential_codes:
        if code in CPV_CODES and not any(cpv['code'] == code for cpv in found_cpvs):
            found_cpvs.append({
                'code': code,
                'description': CPV_CODES[code],
                'source': 'text_search',
                'validated': True
            })
            logger.debug(f"Found validated CPV code {code} for tender {resource_id}")
    
    if found_cpvs:
        logger.info(f"Extracted {len(found_cpvs)} CPV codes for tender {resource_id}")
    else:
        logger.debug(f"No CPV codes found for tender {resource_id}")
    
    return found_cpvs


def check_cpv_codes(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check and enrich record with CPV code information.
    
    Args:
        record: Tender record dictionary
        
    Returns:
        Record enriched with cpv_codes field
    """
    enriched = record.copy()
    
    cpv_codes = extract_cpv_codes(record)
    
    enriched['cpv_codes'] = cpv_codes
    enriched['cpv_count'] = len(cpv_codes)
    enriched['has_validated_cpv'] = any(cpv['validated'] for cpv in cpv_codes)
    
    # Create simple list of just the codes
    enriched['cpv_code_list'] = [cpv['code'] for cpv in cpv_codes]
    
    return enriched


def get_cpv_summary(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get summary of CPV codes for a record.
    
    Args:
        record: Tender record with cpv_codes field
        
    Returns:
        Summary dictionary with resource_id, count, and codes
    """
    return {
        'resource_id': record.get('resource_id'),
        'title': record.get('title'),
        'cpv_count': record.get('cpv_count', 0),
        'cpv_codes': record.get('cpv_code_list', []),
        'cpv_details': record.get('cpv_codes', [])
    }


if __name__ == "__main__":
    # Test CPV checker with sample data
    test_record = {
        'resource_id': '5196306',
        'title': 'Security Software Framework',
        'info': 'Software consultancy 72000000',
        'pdf_data': {
            'main_classification': '72212731 File security software development services'
        }
    }
    
    enriched = check_cpv_codes(test_record)
    summary = get_cpv_summary(enriched)
    
    print("CPV Summary:")
    print(json.dumps(summary, indent=2))
