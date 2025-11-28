"""
PDF parser that enriches tender records with parsed PDF data.
Accepts a tender record, extracts PDF text if URL exists, parses with local Ollama LLM.
"""

import logging
import requests
from io import BytesIO
from pdfminer.high_level import extract_text
import json
import re
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize error log file
PDF_ERROR_LOG = 'pdf_parser_errors.log'


def log_error(message: str):
    """Write error message to log file and print to console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    try:
        with open(PDF_ERROR_LOG, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except:
        pass  # Fail silently if can't write to log
    
    print(message)


def extract_pdf_text(pdf_url: str) -> str:
    """
    Extract text content from a PDF URL.
    
    Args:
        pdf_url: URL to the PDF file
        
    Returns:
        Extracted text content or empty string on error
    """
    try:
        logger.info(f"Downloading PDF from: {pdf_url}")
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        
        pdf_size = len(response.content)
        logger.debug(f"PDF downloaded: {pdf_size} bytes")
        
        pdf_file = BytesIO(response.content)
        text = extract_text(pdf_file)
        
        text_length = len(text)
        logger.info(f"Successfully extracted {text_length} characters from PDF")
        
        return text
        
    except requests.RequestException as e:
        logger.error(f"Failed to download PDF from {pdf_url}: {e}")
        log_error(f"Error downloading PDF from {pdf_url}: {e}")
        return ''
    except Exception as e:
        logger.error(f"Error extracting text from PDF {pdf_url}: {e}", exc_info=True)
        log_error(f"Error extracting PDF from {pdf_url}: {e}")
        return ''


def parse_pdf_with_ollama(text_content: str, model: str = "llama3.2:3b", debug: bool = False) -> Dict[str, Any]:
    """
    Parse PDF text using local Ollama LLM to extract structured metadata AND organize full content by headings.
    
    Args:
        text_content: Extracted PDF text
        model: Ollama model to use (default: llama3.2:3b)
        debug: If True, save problematic responses to debug_ollama_response.json
        
    Returns:
        Parsed tender data with metadata fields and full pdf_content organized by headings
    """
    prompt = """Analyze this tender PDF and extract two things:

1. METADATA - Extract these specific fields:
{
  "procedure_id": "",
  "title": "",
  "buyer_name": "",
  "buyer_country": "",
  "estimated_value": "",
  "start_date": "",
  "duration_months": "",
  "submission_deadline": "",
  "main_classification": "",
  "lots": []
}

2. PDF_CONTENT - Organize ALL the text content by its headings/sections. Create a dictionary where:
   - Keys are the heading/section names (e.g., "Section_I_Contracting_Authority", "Technical_Requirements", "Award_Criteria")
   - Values are the full text under that heading
   - If no clear headings exist, use logical section names like "Overview", "Requirements", "Submission_Details"

Return as JSON:
{
  "metadata": { ... fields above ... },
  "pdf_content": {
    "heading1_name": "full text under this heading",
    "heading2_name": "full text under this heading",
    ...
  }
}

PDF Text:
""" + text_content[:15000]  # Increased limit to capture more content
    
    try:
        # Call Ollama API
        logger.info(f"Parsing PDF content with Ollama model: {model}")
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'stream': False,
                'format': 'json'  # Request JSON output
            },
            timeout=90  # Increased timeout for more complex parsing
        )
        response.raise_for_status()
        
        result = response.json()
        response_text = result.get('response', '')
        logger.debug(f"Ollama response length: {len(response_text)} characters")
        
        # Parse JSON from response
        # Remove markdown code blocks if present
        json_text = re.sub(r'^```json\s*\n', '', response_text)
        json_text = re.sub(r'\n```\s*$', '', json_text)
        json_text = re.sub(r'^```\s*\n', '', json_text)
        json_text = json_text.strip()
        
        try:
            parsed = json.loads(json_text)
            logger.info("Successfully parsed Ollama JSON response")
        except json.JSONDecodeError as je:
            # Log the problematic JSON for debugging
            logger.error(f"JSON Parse Error at line {je.lineno}, column {je.colno}: {je.msg}")
            log_error(f"✗ JSON Parse Error at line {je.lineno}, column {je.colno}")
            log_error(f"  Error: {je.msg}")
            log_error(f"  Problematic JSON (first 500 chars):")
            log_error(f"  {json_text[:500]}")
            
            # Save to debug file if debug mode enabled
            if debug:
                import os
                debug_file = f'debug_ollama_response_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                with open(debug_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'error': str(je),
                        'raw_response': response_text,
                        'cleaned_json': json_text,
                        'pdf_text_preview': text_content[:1000]
                    }, f, indent=2)
                print(f"  Debug info saved to {debug_file}")
            
            # Try to fix common JSON issues
            # 1. Replace single quotes with double quotes
            json_text_fixed = json_text.replace("'", '"')
            
            # 2. Try to extract just the JSON object if there's extra text
            json_match = re.search(r'\{.*\}', json_text_fixed, re.DOTALL)
            if json_match:
                json_text_fixed = json_match.group(0)
                try:
                    parsed = json.loads(json_text_fixed)
                    log_error("  ✓ Recovered with quote fix")
                except:
                    # Still failed - return raw text fallback
                    log_error("  ✗ Could not recover - using raw text fallback")
                    return {
                        'pdf_content': {
                            'full_text': text_content[:15000],
                            'parse_error': str(je)
                        }
                    }
            else:
                # No JSON found - return raw text
                return {
                    'pdf_content': {
                        'full_text': text_content[:15000],
                        'parse_error': str(je)
                    }
                }
        
        # Flatten structure - merge metadata fields with pdf_content
        result_data = parsed.get('metadata', {})
        result_data['pdf_content'] = parsed.get('pdf_content', {})
        
        # If parsing failed to organize content, include raw text as fallback
        if not result_data.get('pdf_content'):
            result_data['pdf_content'] = {
                'full_text': text_content[:15000]
            }
        
        return result_data
        
    except requests.exceptions.ConnectionError:
        logger.error("Ollama connection failed - service not running")
        log_error("✗ Error: Ollama not running. Start it with: ollama serve")
        return {}
    except Exception as e:
        logger.error(f"Error parsing with Ollama: {e}", exc_info=True)
        log_error(f"Error parsing with Ollama: {e}")
        # Return raw text as fallback
        return {
            'pdf_content': {
                'full_text': text_content[:15000]
            }
        }


def enrich_record_with_pdf(record: Dict[str, Any], debug: bool = False) -> Dict[str, Any]:
    """
    Enrich tender record with parsed PDF data if PDF URL exists.
    
    Args:
        record: Tender record dictionary
        debug: Enable debug mode to save problematic Ollama responses
        
    Returns:
        Record enriched with pdf_data field containing parsed information
    """
    enriched = record.copy()
    resource_id = record.get('resource_id', 'unknown')
    
    pdf_url = record.get('notice_pdf_url', '')
    
    if not pdf_url:
        logger.debug(f"No PDF URL for tender {resource_id}")
        enriched['pdf_data'] = None
        enriched['pdf_parsed'] = False
        return enriched
    
    logger.info(f"Enriching tender {resource_id} with PDF data")
    
    # Extract PDF text
    text_content = extract_pdf_text(pdf_url)
    
    if not text_content:
        logger.warning(f"Failed to extract text from PDF for tender {resource_id}")
        enriched['pdf_data'] = None
        enriched['pdf_parsed'] = False
        return enriched
    
    # Parse with Ollama
    parsed_data = parse_pdf_with_ollama(text_content, debug=debug)
    
    if parsed_data:
        logger.info(f"Successfully enriched tender {resource_id} with PDF data")
        enriched['pdf_data'] = parsed_data
        enriched['pdf_parsed'] = True
    else:
        logger.warning(f"Failed to parse PDF data for tender {resource_id}")
        enriched['pdf_data'] = None
        enriched['pdf_parsed'] = False
    
    return enriched


if __name__ == "__main__":
    # Test PDF enrichment
    test_record = {
        'resource_id': '5196306',
        'title': 'Security Software Framework',
        'notice_pdf_url': 'https://www.etenders.gov.ie/epps/cft/downloadNoticeForAdvSearch.do?resourceId=5196306'
    }
    
    enriched = enrich_record_with_pdf(test_record)
    
    print("Enriched record:")
    print(json.dumps(enriched, indent=2))

