"""
AI Bid Analyzer - Uses Ollama to determine if IT consultancy should bid on tender
"""

import requests
import json
from typing import Dict, Any, List
from datetime import datetime


def analyze_tender_for_bid(combined_record: Dict[str, Any], model: str = "llama3.2:3b") -> Dict[str, Any]:
    """
    Analyze a combined tender record to determine if IT consultancy should bid.
    
    Args:
        combined_record: Combined record with tender, pdf, and cpv data
        model: Ollama model to use
        
    Returns:
        Analysis result with bid recommendation and reasoning
    """
    # Build context for AI
    tender = combined_record.get('tender', {})
    pdf = combined_record.get('pdf', {})
    cpv = combined_record.get('cpv', {})
    
    # Extract PDF content sections for detailed analysis
    pdf_content = pdf.get('pdf_content', {}) if pdf else {}
    pdf_sections = "\n".join([f"{heading}: {text[:500]}..." for heading, text in pdf_content.items()]) if pdf_content else "No PDF content available"
    
    context = f"""
You are a bid qualification analyst for Version 1, a technology consultancy company.

TENDER DETAILS:
Title: {tender.get('title', 'N/A')}
Contracting Authority: {tender.get('contracting_authority', 'N/A')}
Estimated Value: {tender.get('estimated_value', 'N/A')}
Info: {tender.get('info', 'N/A')}
Main Classification: {pdf.get('main_classification', 'N/A') if pdf else 'N/A'}
CPV Codes: {cpv.get('cpv_codes', []) if cpv else []}

FULL PDF CONTENT (organized by sections):
{pdf_sections}

STRICT IT-RELATED REQUIREMENTS - Must match at least ONE:
1. Software/Application Development or Modernisation
2. Cloud Infrastructure, Migration, or Services (AWS, Azure, Oracle Cloud)
3. Data Platforms, Analytics, Business Intelligence, or AI/ML
4. Enterprise Software (Oracle, SAP, Microsoft Dynamics, Salesforce)
5. IT Infrastructure, Networking, or Cybersecurity Services
6. Digital Services, Web/Mobile Applications, or Portals
7. IT Consulting, Architecture, or Strategy
8. Managed IT Services or Support
9. Software License Management or FinOps
10. Contains a CPV code from the known IT/software CPV list

IMMEDIATE DISQUALIFICATION - Automatically reject if ANY apply:
❌ Physical goods ONLY (furniture, equipment, vehicles, supplies, trees, ice machines)
❌ Construction, facilities, or building works
❌ Catering, food services, or meals
❌ Cleaning, maintenance, or janitorial services  
❌ Medical equipment or healthcare supplies
❌ Educational materials, toys, or books (unless digital/software)
❌ Agricultural products or farming equipment
❌ Transportation or logistics services
❌ Paper printing or publishing services
❌ Legal, HR, or recruitment services (unless for IT roles)
❌ Marketing, PR, or creative services (unless digital platform development)
❌ Generic consultancy with no IT/technology component

DECISION PROCESS:
Step 1: Read the tender title carefully - does it mention software, IT, technology, cloud, data, digital, or systems?
Step 2: Check if it's purely physical goods or non-IT services - if yes, REJECT immediately
Step 3: Look for IT keywords: application, platform, infrastructure, database, API, integration, modernisation
Step 4: If unsure, default to REJECT unless clear IT/technology evidence exists

Version 1 is a TECHNOLOGY company. We do NOT bid on:
- Furniture, fixtures, or physical fit-outs
- Food or catering services
- Building or construction work
- Physical product procurement
- Non-technology professional services

Return ONLY valid JSON:
{{
  "should_bid": false,
  "confidence": "high",
  "reasoning": "Specific reason - if rejecting non-IT, state clearly what physical/non-IT service it is",
  "relevant_factors": ["Primary reason for decision"],
  "estimated_fit": "0"
}}

If truly IT-related and matches Version 1's capabilities, set should_bid to true with fit score 60-100.
"""
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': context,
                'stream': False,
                'format': 'json'
            },
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        response_text = result.get('response', '')
        
        # Parse JSON response
        import re
        json_text = re.sub(r'^```json\s*\n', '', response_text)
        json_text = re.sub(r'\n```\s*$', '', json_text)
        json_text = json_text.strip()
        
        analysis = json.loads(json_text)
        
        # Add metadata
        analysis['resource_id'] = combined_record.get('resource_id')
        analysis['analyzed_at'] = datetime.now().isoformat()
        
        return analysis
        
    except requests.exceptions.ConnectionError:
        print("✗ Error: Ollama not running. Start it with: ollama serve")
        return {
            'resource_id': combined_record.get('resource_id'),
            'should_bid': False,
            'confidence': 'low',
            'reasoning': 'Analysis failed - Ollama not running',
            'error': True
        }
    except Exception as e:
        print(f"Error analyzing tender {combined_record.get('resource_id')}: {e}")
        return {
            'resource_id': combined_record.get('resource_id'),
            'should_bid': False,
            'confidence': 'low',
            'reasoning': f'Analysis failed: {str(e)}',
            'error': True
        }


def batch_analyze_tenders(combined_records: List[Dict[str, Any]], 
                          model: str = "llama3.2:3b",
                          output_file: str = None) -> None:
    """
    Analyze multiple tenders for bid recommendations.
    Streams results to file to avoid memory issues with large datasets.
    
    Args:
        combined_records: List of combined tender records (can be generator)
        model: Ollama model to use
        output_file: Optional output file to stream results to
    """
    import os
    from json_output import JSONOutput
    from csv_output import CSVOutput
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directories
    os.makedirs('outputs/json', exist_ok=True)
    os.makedirs('outputs/csv', exist_ok=True)
    
    # Initialize streaming outputs
    json_output = JSONOutput(f'outputs/json/bid_analysis_{timestamp}.json', streaming=True)
    csv_output = CSVOutput(f'outputs/csv/bid_analysis_{timestamp}.csv', streaming=True)
    
    total = len(combined_records) if hasattr(combined_records, '__len__') else 0
    
    print(f"\nAnalyzing tenders for bid opportunities...")
    print("=" * 60)
    
    bid_count = 0
    processed = 0
    
    try:
        for idx, record in enumerate(combined_records, 1):
            resource_id = record.get('resource_id', 'unknown')
            print(f"[{idx}] Analyzing tender {resource_id}...", end=' ')
            
            analysis = analyze_tender_for_bid(record, model)
            
            # Write immediately to both outputs
            json_output.write_record(analysis)
            csv_output.write_record(analysis)
            
            processed += 1
            
            # Show result
            if analysis.get('should_bid'):
                bid_count += 1
                print(f"✓ BID ({analysis.get('confidence', 'unknown')} confidence)")
            else:
                print(f"✗ SKIP")
            
            # Periodic progress for large datasets
            if processed % 50 == 0:
                print(f"  Progress: {processed} processed, {bid_count} bids recommended")
    
    finally:
        # Flush outputs
        json_output.flush()
        csv_output.flush()
    
    print("=" * 60)
    print(f"\nRecommendations: {bid_count}/{processed} tenders worth bidding on")
    print(f"Results saved to:")
    print(f"  - outputs/json/bid_analysis_{timestamp}.json")
    print(f"  - outputs/csv/bid_analysis_{timestamp}.csv")


def save_bid_analysis(analyses: List[Dict[str, Any]], 
                      output_format: str = 'json',
                      output_file: str = None) -> None:
    """
    Save bid analysis results to file.
    
    Args:
        analyses: List of analysis results
        output_format: 'json' or 'csv'
        output_file: Output file path (auto-generated if not provided)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if output_format == 'json':
        output_file = output_file or f'bid_analysis_{timestamp}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analyses, f, indent=2)
        print(f"✓ Saved analysis to {output_file}")
        
    elif output_format == 'csv':
        output_file = output_file or f'bid_analysis_{timestamp}.csv'
        
        import csv
        fieldnames = ['resource_id', 'should_bid', 'confidence', 'reasoning', 
                     'estimated_fit', 'analyzed_at']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for analysis in analyses:
                # Flatten relevant_factors if it exists
                row = analysis.copy()
                if 'relevant_factors' in row and isinstance(row['relevant_factors'], list):
                    row['relevant_factors'] = ', '.join(row['relevant_factors'])
                writer.writerow(row)
        
        print(f"✓ Saved analysis to {output_file}")


if __name__ == "__main__":
    # Test with combined data
    from data_combiner import combine_data
    import glob
    
    # Find most recent files
    tender_files = sorted(glob.glob('outputs/csv/tenders_*.csv'), reverse=True)
    pdf_files = sorted(glob.glob('outputs/csv/pdfs_*.csv'), reverse=True)
    cpv_files = sorted(glob.glob('outputs/csv/cpvs_*.csv'), reverse=True)
    
    if tender_files:
        print("Loading combined data...")
        combined = combine_data(
            'csv',
            tenders_file=tender_files[0],
            pdfs_file=pdf_files[0] if pdf_files else 'pdfs.csv',
            cpvs_file=cpv_files[0] if cpv_files else 'cpvs.csv'
        )
        
        # Analyze all tenders (streaming output)
        batch_analyze_tenders(combined)
    else:
        print("No tender files found. Run the pipeline first.")
