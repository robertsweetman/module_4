"""
AI Bid Analyzer - Uses Ollama to determine if IT consultancy should bid on tender
"""

import logging
import requests
import json
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


def analyze_tender_for_bid(combined_record: Dict[str, Any], model: str = "llama3.1:8b") -> Dict[str, Any]:
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
    
    resource_id = combined_record.get('resource_id', 'unknown')
    
    # Parse CPV codes if they're strings (from CSV)
    cpv_codes = cpv.get('cpv_codes', []) if cpv else []
    if isinstance(cpv_codes, str):
        import ast
        try:
            cpv_codes = ast.literal_eval(cpv_codes)
        except:
            cpv_codes = []
    
    cpv_count = cpv.get('cpv_count', 0) if cpv else 0
    has_validated = cpv.get('has_validated_cpv', False) if cpv else False
    
    logger.info(f"Analyzing tender {resource_id}: {cpv_count} CPV codes found, validated={has_validated}")
    
    # Extract PDF content sections for detailed analysis
    pdf_content = pdf.get('pdf_content', {}) if pdf else {}
    
    # Handle both dict and JSON string formats
    if isinstance(pdf_content, str):
        import json
        try:
            pdf_content = json.loads(pdf_content) if pdf_content else {}
        except (json.JSONDecodeError, ValueError):
            pdf_content = {}
    
    # Include FULL PDF content, not truncated
    pdf_sections = "\n".join([
        f"{heading}: {str(text)}" 
        for heading, text in pdf_content.items() 
        if text and str(text).strip()
    ]) if pdf_content else "No PDF content available"
    
    context = f"""
You are a bid qualification analyst for Version 1, a technology consultancy company specializing in enterprise software, cloud services, data platforms, and IT modernization.

TENDER DETAILS:
Title: {tender.get('title', 'N/A')}
Contracting Authority: {tender.get('contracting_authority', 'N/A')}
Estimated Value: {tender.get('estimated_value', 'N/A')}
Info: {tender.get('info', 'N/A')}
Main Classification: {pdf.get('main_classification', 'N/A') if pdf else 'N/A'}
CPV Codes Found: {cpv_count}
CPV Codes: {cpv_codes}
Has Validated IT/Software CPV: {has_validated}

FULL PDF CONTENT (all sections):
{pdf_sections}

TENDER SHOULD BE RECOMMENDED (should_bid=true) IF IT INCLUDES ANY OF:
✓ Software development, customization, or modernization
✓ Cloud infrastructure, migration, or managed services (AWS, Azure, GCP, Oracle Cloud)
✓ Data platforms, analytics, business intelligence, AI/ML, or data science
✓ Enterprise software implementation (Oracle, SAP, Microsoft Dynamics, Salesforce, etc.)
✓ IT infrastructure design, networking, or cybersecurity
✓ Digital transformation, web/mobile applications, portals, or digital services
✓ IT consulting, architecture, strategy, or advisory services
✓ Managed IT services, application support, or DevOps
✓ Software license management, FinOps, or IT governance
✓ IT hardware procurement WITH significant software/services component
✓ System integration, API development, or middleware
✓ Database design, administration, or optimization

TENDER CAN BE REJECTED (should_bid=false) IF IT IS CLEARLY:
❌ Pure physical goods with NO IT services (furniture, office supplies, vehicles, catering equipment)
❌ Construction or building works with NO IT/digital component
❌ Food, catering, or hospitality services
❌ Cleaning or janitorial services
❌ Pure medical supplies or pharmaceuticals (not healthcare IT systems)
❌ Agricultural products or farming equipment
❌ Transportation or logistics operations (not logistics software)
❌ Printing or publishing (not digital publishing platforms)
❌ HR/recruitment for non-IT roles
❌ Generic management consulting with NO technology component

IMPORTANT CONSIDERATIONS:
- IT hardware tenders are ACCEPTABLE if they include implementation, integration, or support services
- Tenders mentioning "software", "cloud", "data", "digital", "systems", "IT", or "technology" should be considered carefully
- Mixed tenders (hardware + software + services) are GOOD candidates
- If a tender has validated IT CPV codes, strongly consider recommending it
- When in doubt about IT relevance, err on the side of recommendation (we can filter later)

DECISION PROCESS:
1. Check title and main classification for IT/technology keywords
2. Review full PDF content for technical requirements, software mentions, IT services
3. Consider validated CPV codes - if true, this is strong evidence for recommendation
4. Assess if Version 1's capabilities (software, cloud, data, IT consulting) match the tender
5. If there's ANY significant IT component, recommend the bid

Return ONLY valid JSON:
{{
  "should_bid": true/false,
  "confidence": "high/medium/low",
  "reasoning": "Clear explanation of why this tender is/isn't a good fit for Version 1",
  "relevant_factors": ["Key factors that influenced the decision"],
  "estimated_fit": "0-100 (how well this matches Version 1's capabilities)"
}}

For IT-related tenders, set estimated_fit to 60-100 based on alignment with Version 1's expertise.
For non-IT tenders, set estimated_fit to 0-30.
"""
    
    try:
        logger.debug(f"Sending bid analysis request to Ollama for tender {resource_id}")
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
        logger.debug(f"Received analysis response for tender {resource_id}")
        
        # Parse JSON response
        import re
        json_text = re.sub(r'^```json\s*\n', '', response_text)
        json_text = re.sub(r'\n```\s*$', '', json_text)
        json_text = json_text.strip()
        
        analysis = json.loads(json_text)
        
        # Convert string values to numeric for database compatibility
        # confidence: "high" -> 0.90, "medium" -> 0.60, "low" -> 0.30
        confidence_str = str(analysis.get('confidence', 'low')).lower()
        if confidence_str == 'high':
            analysis['confidence'] = 0.90
        elif confidence_str == 'medium':
            analysis['confidence'] = 0.60
        else:
            analysis['confidence'] = 0.30
        
        # estimated_fit: string number to float (0-100 scale, convert to 0-1 scale)
        try:
            fit_value = float(str(analysis.get('estimated_fit', '0')))
            # If value is > 1, assume it's on 0-100 scale, convert to 0-1
            if fit_value > 1:
                fit_value = fit_value / 100.0
            analysis['estimated_fit'] = min(max(fit_value, 0.0), 1.0)  # Clamp to 0-1
        except (ValueError, TypeError):
            analysis['estimated_fit'] = 0.0
        
        # Add metadata
        analysis['resource_id'] = combined_record.get('resource_id')
        analysis['analyzed_at'] = datetime.now().isoformat()
        
        should_bid = analysis.get('should_bid', False)
        confidence = analysis.get('confidence')
        logger.info(f"Tender {resource_id} analysis: should_bid={should_bid}, confidence={confidence}")
        
        return analysis
        
    except requests.exceptions.ConnectionError:
        logger.error("Ollama connection failed - service not running")
        print("✗ Error: Ollama not running. Start it with: ollama serve")
        return {
            'resource_id': combined_record.get('resource_id'),
            'should_bid': False,
            'confidence': 0.30,
            'reasoning': 'Analysis failed - Ollama not running',
            'estimated_fit': 0.0,
            'error': True
        }
    except Exception as e:
        logger.error(f"Error analyzing tender {resource_id}: {e}", exc_info=True)
        print(f"Error analyzing tender {resource_id}: {e}")
        return {
            'resource_id': combined_record.get('resource_id'),
            'should_bid': False,
            'confidence': 0.30,
            'reasoning': f'Analysis failed: {str(e)}',
            'estimated_fit': 0.0,
            'error': True
        }
        return {
            'resource_id': resource_id,
            'should_bid': False,
            'confidence': 'low',
            'reasoning': f'Analysis failed: {str(e)}',
            'error': True
        }


def batch_analyze_tenders(combined_records: List[Dict[str, Any]], 
                          model: str = "llama3.1:8b",
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
    
    logger.info("Starting batch bid analysis")
    logger.info(f"Output files: outputs/json/bid_analysis_{timestamp}.json and CSV")
    
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
    
    logger.info("="*80)
    logger.info(f"Batch analysis complete: {bid_count}/{processed} tenders recommended for bidding")
    logger.info(f"Results saved to outputs/json/bid_analysis_{timestamp}.json and CSV")
    logger.info("="*80)
    
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
