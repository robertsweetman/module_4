"""
Main pipeline orchestrator for eTenders scraping and processing
Configurable data pipeline with modular processing stages
"""

import argparse
import logging
import sys
from typing import Generator, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def setup_logging(enable_logging: bool = False) -> str:
    """
    Configure logging if enabled.
    
    Args:
        enable_logging: Whether to enable logging to file and console
        
    Returns:
        Log filename if logging enabled, empty string otherwise
    """
    if enable_logging:
        log_filename = f'etenders_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logger.info(f"Logging enabled to: {log_filename}")
        return log_filename
    else:
        # Disable all logging
        logging.basicConfig(level=logging.CRITICAL + 1)
        return ''

# Import pipeline stages
from etenders_scraper import scrape_pages
from type_coercer import coerce_types
from pdf_parser import enrich_record_with_pdf
from cpv_list_checker import check_cpv_codes

# Import output handlers
from json_output import JSONOutput
from csv_output import CSVOutput
from postgres_output import PostgresOutput


def process_record(record: Dict[str, Any], 
                   process_pdfs: bool = True,
                   check_cpvs: bool = True,
                   debug: bool = False) -> tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """
    Process a single record through the pipeline.
    Returns three separate records for different output tables.
    
    Args:
        record: Raw tender record from scraper
        process_pdfs: Whether to extract and parse PDFs
        check_cpvs: Whether to check CPV codes
        
    Returns:
        Tuple of (tender_record, pdf_record, cpv_record)
    """
    # Stage 1: Type coercion - creates tender record
    tender_record = coerce_types(record)
    resource_id = tender_record.get('resource_id')
    logger.debug(f"Processing tender ID: {resource_id}")
    
    # Stage 2: PDF parsing - creates separate PDF record
    pdf_record = None
    enriched = tender_record  # Default to tender_record if no PDF processing
    if process_pdfs and tender_record.get('has_pdf_url'):
        logger.debug(f"Processing PDF for tender {resource_id}")
        enriched = enrich_record_with_pdf(tender_record, debug=debug)
        if enriched.get('pdf_parsed') and enriched.get('pdf_data'):
            import json
            pdf_data = enriched['pdf_data']
            # Convert pdf_content dict to JSON string
            pdf_content_str = json.dumps(pdf_data.get('pdf_content', {})) if isinstance(pdf_data.get('pdf_content'), dict) else str(pdf_data.get('pdf_content', ''))
            
            pdf_record = {
                'resource_id': resource_id,
                'pdf_url': tender_record.get('notice_pdf_url'),
                'pdf_parsed': True,
                'pdf_content': pdf_content_str
            }
            logger.info(f"Successfully parsed PDF for tender {resource_id}")
        else:
            logger.warning(f"Failed to parse PDF for tender {resource_id}")
    
    # Stage 3: CPV code checking - creates separate CPV record
    # Use enriched record which has PDF data with CPV codes
    cpv_record = None
    if check_cpvs:
        enriched_cpv = check_cpv_codes(enriched)
        cpv_count = enriched_cpv.get('cpv_count', 0)
        
        # Always create CPV record if any codes found (including validated IT codes)
        if cpv_count > 0:
            cpv_record = {
                'resource_id': resource_id,
                'cpv_count': cpv_count,
                'cpv_codes': enriched_cpv.get('cpv_code_list', []),
                'cpv_details': enriched_cpv.get('cpv_codes', []),
                'has_validated_cpv': enriched_cpv.get('has_validated_cpv', False)
            }
            validated_count = len([c for c in enriched_cpv.get('cpv_codes', []) if c.get('validated')])
            logger.info(f"Found {cpv_count} CPV codes for tender {resource_id} ({validated_count} validated IT codes)")
        else:
            logger.debug(f"No CPV codes found for tender {resource_id}")
    
    return tender_record, pdf_record, cpv_record


def run_pipeline(start_page: int = 1,
                end_page: int = 1,
                output_format: str = 'json',
                output_file: str = None,
                process_pdfs: bool = True,
                check_cpvs: bool = True,
                delay: float = 1.0,
                debug: bool = False,
                enable_logging: bool = False,
                analyze_bids: bool = False) -> tuple[str, str, str, str]:
    """
    Run the complete eTenders scraping and processing pipeline
    
    Args:
        start_page: First page to scrape
        end_page: Last page to scrape
        output_format: Output format ('json', 'csv', or 'postgres')
        output_file: Base filename for output (auto-generated if None)
        process_pdfs: Whether to download and parse PDFs
        check_cpvs: Whether to check CPV codes
        delay: Delay between requests in seconds
        debug: Enable debug mode for LLM responses
        enable_logging: Enable logging to file and console
        
    Returns:
        Tuple of (timestamp, tenders_output, pdfs_output, cpvs_output)
    """
    # Setup logging
    log_file = setup_logging(enable_logging)
    if log_file:
        logger.info(f"Logging enabled to: {log_file}")
        print(f"Logging enabled: {log_file}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Initialize output handlers based on format
    if output_format == 'postgres':
        # PostgresOutput doesn't need table_name parameter
        output_handler = PostgresOutput()
        logger.info("Using PostgreSQL output")
    elif output_format == 'csv':
        output_handler = CSVOutput(timestamp=timestamp, base_filename=output_file)
        logger.info(f"Using CSV output with timestamp: {timestamp}")
    else:  # json
        output_handler = JSONOutput(timestamp=timestamp, base_filename=output_file)
        logger.info(f"Using JSON output with timestamp: {timestamp}")
    
    # Collect records
    tender_records = []
    pdf_records = []
    cpv_records = []
    bid_records = []
    
    # Batch size for incremental writes (write every N records)
    BATCH_SIZE = 10
    total_written = {'tenders': 0, 'pdfs': 0, 'cpvs': 0, 'bids': 0}
    
    # Import bid analyzer if needed
    if analyze_bids and output_format == 'postgres':
        from bid_analyzer import analyze_tender_for_bid
    
    logger.info(f"Starting scraping from page {start_page} to {end_page}")
    print(f"\nScraping eTenders pages {start_page} to {end_page}...")
    
    # Scrape and process records
    for i, record in enumerate(scrape_pages(start_page=start_page, end_page=end_page, delay=delay), start=1):
        # Process each record
        tender_data, pdf_data, cpv_data = process_record(
            record, 
            process_pdfs=process_pdfs,
            check_cpvs=check_cpvs,
            debug=debug
        )
        
        tender_records.append(tender_data)
        
        if pdf_data:
            pdf_records.append(pdf_data)
        
        if cpv_data:
            cpv_records.append(cpv_data)
        
        # Analyze bid immediately if enabled (before batching)
        if analyze_bids and output_format == 'postgres' and pdf_data:
            # Structure data to match bid_analyzer's expected format
            analysis_data = {
                'resource_id': tender_data.get('resource_id'),
                'tender': tender_data,
                'pdf': pdf_data,
                'cpv': cpv_data if cpv_data else {}
            }
            bid_analysis = analyze_tender_for_bid(analysis_data)
            if bid_analysis:
                bid_analysis['resource_id'] = tender_data.get('resource_id')
                bid_records.append(bid_analysis)
                logger.info(f"Analyzed bid for {tender_data.get('resource_id')}")
        
        # Write in batches for postgres output
        if output_format == 'postgres' and i % BATCH_SIZE == 0:
            logger.info(f"Writing batch of {len(tender_records)} records to database...")
            result = output_handler.write_records(
                tender_records=tender_records,
                pdf_records=pdf_records,
                cpv_records=cpv_records,
                bid_records=bid_records  # Write bid analyses in same batch
            )
            batch_tenders, batch_pdfs, batch_cpvs, batch_bids = result
            total_written['tenders'] += batch_tenders
            total_written['pdfs'] += batch_pdfs
            total_written['cpvs'] += batch_cpvs
            total_written['bids'] += batch_bids
            
            print(f"✓ Wrote batch: {batch_tenders} tenders, {batch_pdfs} PDFs, {batch_cpvs} CPVs, {batch_bids} bid analyses (total: {total_written['tenders']} tenders)")
            
            # Clear batch
            tender_records = []
            pdf_records = []
            cpv_records = []
            bid_records = []
    
    # Write any remaining records
    if output_format == 'postgres' and tender_records:
        logger.info(f"Writing final batch of {len(tender_records)} records...")
        result = output_handler.write_records(
            tender_records=tender_records,
            pdf_records=pdf_records,
            cpv_records=cpv_records,
            bid_records=bid_records
        )
        batch_tenders, batch_pdfs, batch_cpvs, batch_bids = result
        total_written['tenders'] += batch_tenders
        total_written['pdfs'] += batch_pdfs
        total_written['cpvs'] += batch_cpvs
        total_written['bids'] += batch_bids
        print(f"✓ Wrote final batch: {batch_tenders} tenders, {batch_pdfs} PDFs, {batch_cpvs} CPVs, {batch_bids} bid analyses")
    
    logger.info(f"Scraped {total_written.get('tenders', len(tender_records))} tender records")
    print(f"\n✓ Total scraped: {total_written.get('tenders', len(tender_records))} tenders")
    if analyze_bids and output_format == 'postgres':
        print(f"✓ Total analyzed: {total_written.get('bids', 0)} bids")
    
    # Final summary
    if output_format == 'postgres':
        output_handler.close()
        
        logger.info(f"PostgreSQL write complete: {total_written['tenders']} tenders, {total_written['pdfs']} PDFs, {total_written['cpvs']} CPVs")
        print(f"\n✓ Database Summary:")
        print(f"  - {total_written['tenders']} tenders")
        print(f"  - {total_written['pdfs']} PDFs")
        print(f"  - {total_written['cpvs']} CPV records")
        
        return timestamp, total_written['tenders'], total_written['pdfs'], total_written['cpvs']
    
    else:
        # CSV or JSON output - write all at once at the end
        tenders_file = output_handler.write_tenders(tender_records)
        pdfs_file = output_handler.write_pdfs(pdf_records)
        cpvs_file = output_handler.write_cpvs(cpv_records)
        
        logger.info(f"Files written: {tenders_file}, {pdfs_file}, {cpvs_file}")
        print(f"\n✓ Output files created:")
        print(f"  - {tenders_file}")
        print(f"  - {pdfs_file}")
        print(f"  - {cpvs_file}")
        
        return timestamp, tenders_file, pdfs_file, cpvs_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='eTenders scraping and processing pipeline')
    
    parser.add_argument('--start-page', type=int, default=1,
                       help='First page to scrape (default: 1)')
    parser.add_argument('--end-page', type=int, default=1,
                       help='Last page to scrape (default: 1)')
    parser.add_argument('--output', type=str, choices=['json', 'csv', 'postgres'], default='json',
                       help='Output format (default: json)')
    parser.add_argument('--output-file', type=str,
                       help='Output file path (for json/csv only)')
    parser.add_argument('--no-pdfs', action='store_true',
                       help='Disable PDF processing')
    parser.add_argument('--no-cpvs', action='store_true',
                       help='Disable CPV code checking')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between page requests in seconds (default: 1.0)')
    parser.add_argument('--analyze-bids', action='store_true',
                       help='Run AI bid analysis after scraping')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode - saves problematic Ollama responses to files')
    parser.add_argument('--enable-logging', action='store_true',
                       help='Enable logging to file and console (default: disabled)')
    
    args = parser.parse_args()
    
    # Setup logging based on flag
    log_filename = setup_logging(args.enable_logging)
    if log_filename:
        print(f"Logging enabled: {log_filename}")
    
    timestamp, tenders_file, pdfs_file, cpvs_file = run_pipeline(
        start_page=args.start_page,
        end_page=args.end_page,
        output_format=args.output,
        output_file=args.output_file,
        process_pdfs=not args.no_pdfs,
        check_cpvs=not args.no_cpvs,
        debug=args.debug,
        delay=args.delay,
        enable_logging=args.enable_logging,
        analyze_bids=args.analyze_bids
    )
    
    # Note: Bid analysis now runs inline during scraping when --analyze-bids is set
    # No post-processing needed as results are written to database in real-time
