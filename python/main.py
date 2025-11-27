"""
Main pipeline orchestrator for eTenders scraping and processing
Configurable data pipeline with modular processing stages
"""

import argparse
from typing import Generator, Dict, Any
from datetime import datetime

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
    
    # Stage 2: PDF parsing - creates separate PDF record
    pdf_record = None
    enriched = tender_record  # Default to tender_record if no PDF processing
    if process_pdfs and tender_record.get('has_pdf_url'):
        enriched = enrich_record_with_pdf(tender_record, debug=debug)
        if enriched.get('pdf_parsed') and enriched.get('pdf_data'):
            pdf_record = {
                'resource_id': resource_id,
                'pdf_url': tender_record.get('notice_pdf_url'),
                'pdf_parsed': True,
                **enriched['pdf_data']  # Unpack PDF data fields
            }
    
    # Stage 3: CPV code checking - creates separate CPV record
    # Use enriched record which has PDF data with CPV codes
    cpv_record = None
    if check_cpvs:
        enriched_cpv = check_cpv_codes(enriched)
        if enriched_cpv.get('cpv_count', 0) > 0:
            cpv_record = {
                'resource_id': resource_id,
                'cpv_count': enriched_cpv['cpv_count'],
                'cpv_codes': enriched_cpv['cpv_code_list'],
                'cpv_details': enriched_cpv['cpv_codes']
            }
    
    return tender_record, pdf_record, cpv_record


def run_pipeline(start_page: int = 1,
                end_page: int = 1,
                output_format: str = 'json',
                output_file: str = None,
                process_pdfs: bool = True,
                check_cpvs: bool = True,
                delay: float = 1.0,
                debug: bool = False) -> tuple[str, str, str, str]:
    """
    Run the full eTenders scraping and processing pipeline.
    Outputs to three separate files/tables: tenders, pdfs, and cpvs.
    
    Args:
        start_page: First page to scrape
        end_page: Last page to scrape
        output_format: Output format ('json', 'csv', or 'postgres')
        output_file: Output file prefix (not used for postgres)
        process_pdfs: Whether to process PDFs
        check_cpvs: Whether to check CPV codes
        delay: Delay between page requests
        debug: Enable debug mode to save problematic Ollama responses
        
    Returns:
        Tuple of (timestamp, tenders_file, pdfs_file, cpvs_file)
    """
    import os
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directories
    if output_format == 'json':
        os.makedirs('outputs/json', exist_ok=True)
        output_dir = 'outputs/json'
    elif output_format == 'csv':
        os.makedirs('outputs/csv', exist_ok=True)
        output_dir = 'outputs/csv'
    
    # Initialize three output handlers for each table
    if output_format == 'json':
        tenders_output = JSONOutput(f'{output_dir}/tenders_{timestamp}.json')
        pdfs_output = JSONOutput(f'{output_dir}/pdfs_{timestamp}.json')
        cpvs_output = JSONOutput(f'{output_dir}/cpvs_{timestamp}.json')
    elif output_format == 'csv':
        tenders_output = CSVOutput(f'{output_dir}/tenders_{timestamp}.csv')
        pdfs_output = CSVOutput(f'{output_dir}/pdfs_{timestamp}.csv')
        cpvs_output = CSVOutput(f'{output_dir}/cpvs_{timestamp}.csv')
    elif output_format == 'postgres':
        tenders_output = PostgresOutput(table_name='tenders')
        pdfs_output = PostgresOutput(table_name='pdfs')
        cpvs_output = PostgresOutput(table_name='cpvs')
        
        # Connect and create tables
        for output in [tenders_output, pdfs_output, cpvs_output]:
            if not output.connect():
                print(f"✗ Failed to connect to database for {output.table_name}. Aborting.")
                return
            output.create_table()
    else:
        raise ValueError(f"Unknown output format: {output_format}")
    
    print(f"\n{'='*60}")
    print(f"eTenders Pipeline Starting")
    print(f"{'='*60}")
    print(f"Pages: {start_page} to {end_page}")
    print(f"Output: {output_format}")
    if output_format != 'postgres':
        print(f"  - Tenders: {output_dir}/tenders_{timestamp}.{output_format}")
        print(f"  - PDFs: {output_dir}/pdfs_{timestamp}.{output_format}")
        print(f"  - CPVs: {output_dir}/cpvs_{timestamp}.{output_format}")
    else:
        print(f"  - Database tables: tenders, pdfs, cpvs")
    print(f"Process PDFs: {process_pdfs}")
    print(f"Check CPVs: {check_cpvs}")
    print(f"{'='*60}\n")
    
    total_records = 0
    tenders_written = 0
    pdfs_written = 0
    cpvs_written = 0
    failed_records = 0
    
    try:
        # Process records from scraper
        for record in scrape_pages(start_page, end_page, delay):
            total_records += 1
            
            try:
                # Process through pipeline - returns 3 records
                tender_record, pdf_record, cpv_record = process_record(record, process_pdfs, check_cpvs, debug)
                
                # Write tender record (always)
                if tenders_output.write_record(tender_record):
                    tenders_written += 1
                else:
                    failed_records += 1
                
                # Write PDF record (if exists)
                if pdf_record:
                    if pdfs_output.write_record(pdf_record):
                        pdfs_written += 1
                
                # Write CPV record (if exists)
                if cpv_record:
                    if cpvs_output.write_record(cpv_record):
                        cpvs_written += 1
                
                # Progress indicator
                if total_records % 10 == 0:
                    print(f"Processed {total_records} records... "
                          f"(Tenders: {tenders_written} | PDFs: {pdfs_written} | CPVs: {cpvs_written})")
                
            except Exception as e:
                failed_records += 1
                print(f"✗ Error processing record {record.get('resource_id')}: {e}")
        
        # Flush all outputs
        tenders_output.flush()
        pdfs_output.flush()
        cpvs_output.flush()
        
    finally:
        # Close connections for postgres
        if output_format == 'postgres':
            tenders_output.close()
            pdfs_output.close()
            cpvs_output.close()
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Pipeline Complete")
    print(f"{'='*60}")
    print(f"Total records processed: {total_records}")
    print(f"Tenders written: {tenders_written}")
    print(f"PDFs written: {pdfs_written}")
    print(f"CPVs written: {cpvs_written}")
    print(f"Failed: {failed_records}")
    print(f"\nOutput Stats:")
    print(f"  Tenders: {tenders_output.get_stats()}")
    print(f"  PDFs: {pdfs_output.get_stats()}")
    print(f"  CPVs: {cpvs_output.get_stats()}")
    print(f"{'='*60}\n")
    
    # Return file paths for potential bid analysis
    if output_format == 'json':
        return timestamp, f'outputs/json/tenders_{timestamp}.json', f'outputs/json/pdfs_{timestamp}.json', f'outputs/json/cpvs_{timestamp}.json'
    elif output_format == 'csv':
        return timestamp, f'outputs/csv/tenders_{timestamp}.csv', f'outputs/csv/pdfs_{timestamp}.csv', f'outputs/csv/cpvs_{timestamp}.csv'
    else:
        return timestamp, 'tenders', 'pdfs', 'cpvs'


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
    
    args = parser.parse_args()
    
    timestamp, tenders_file, pdfs_file, cpvs_file = run_pipeline(
        start_page=args.start_page,
        end_page=args.end_page,
        output_format=args.output,
        output_file=args.output_file,
        process_pdfs=not args.no_pdfs,
        check_cpvs=not args.no_cpvs,
        debug=args.debug,
        delay=args.delay
    )
    
    # Run bid analysis if requested
    if args.analyze_bids:
        print("\n" + "="*60)
        print("Running AI Bid Analysis...")
        print("="*60 + "\n")
        
        from data_combiner import combine_data
        from bid_analyzer import batch_analyze_tenders, save_bid_analysis
        
        # Combine data from the files we just created
        if args.output == 'csv':
            combined = combine_data(
                'csv',
                tenders_file=tenders_file,
                pdfs_file=pdfs_file,
                cpvs_file=cpvs_file
            )
        elif args.output == 'json':
            combined = combine_data(
                'json',
                tenders_file=tenders_file,
                pdfs_file=pdfs_file,
                cpvs_file=cpvs_file
            )
        else:
            import os
            combined = combine_data('postgres', connection_string=os.environ.get('DATABASE_URL'))
        
        # Analyze tenders
        analyses = batch_analyze_tenders(combined)
        
        # Note: Results are already saved by batch_analyze_tenders (streaming mode)
