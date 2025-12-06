"""
PostgreSQL output handler for eTenders data
Writes to PostgreSQL database with proper table relationships
"""

import psycopg2
from psycopg2.extras import Json
import logging
import os
from dotenv import load_dotenv
from typing import Dict, Any, List

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class PostgresOutput:
    """Handle writing records to PostgreSQL database"""
    
    def __init__(self):
        """Initialize PostgreSQL connection from .env file"""
        self.conn = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """Establish database connection using credentials from .env"""
        try:
            self.conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'etenders_db'),
                user=os.getenv('DB_USER', 'etenders_user'),
                password=os.getenv('DB_PASSWORD', 'etenders_pass')
            )
            self.cursor = self.conn.cursor()
            logger.info("Successfully connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def get_connection(self):
        """Return the database connection object"""
        return self.conn
    
    def write_tender(self, record: Dict[str, Any]) -> bool:
        """
        Write tender record to etenders_core table
        
        Args:
            record: Tender data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT INTO etenders_core (
                    resource_id, row_number, title, detail_url, contracting_authority,
                    info, date_published, submission_deadline, procedure, status,
                    notice_pdf_url, award_date, estimated_value, cycle,
                    date_published_parsed, submission_deadline_parsed, award_date_parsed,
                    estimated_value_numeric, cycle_numeric, has_pdf_url,
                    has_estimated_value, is_open
                ) VALUES (
                    %(resource_id)s, %(row_number)s, %(title)s, %(detail_url)s, %(contracting_authority)s,
                    %(info)s, %(date_published)s, %(submission_deadline)s, %(procedure)s, %(status)s,
                    %(notice_pdf_url)s, %(award_date)s, %(estimated_value)s, %(cycle)s,
                    %(date_published_parsed)s, %(submission_deadline_parsed)s, %(award_date_parsed)s,
                    %(estimated_value_numeric)s, %(cycle_numeric)s, %(has_pdf_url)s,
                    %(has_estimated_value)s, %(is_open)s
                )
                ON CONFLICT (resource_id) DO UPDATE SET
                    row_number = EXCLUDED.row_number,
                    title = EXCLUDED.title,
                    detail_url = EXCLUDED.detail_url,
                    contracting_authority = EXCLUDED.contracting_authority,
                    info = EXCLUDED.info,
                    date_published = EXCLUDED.date_published,
                    submission_deadline = EXCLUDED.submission_deadline,
                    procedure = EXCLUDED.procedure,
                    status = EXCLUDED.status,
                    notice_pdf_url = EXCLUDED.notice_pdf_url,
                    award_date = EXCLUDED.award_date,
                    estimated_value = EXCLUDED.estimated_value,
                    cycle = EXCLUDED.cycle,
                    date_published_parsed = EXCLUDED.date_published_parsed,
                    submission_deadline_parsed = EXCLUDED.submission_deadline_parsed,
                    award_date_parsed = EXCLUDED.award_date_parsed,
                    estimated_value_numeric = EXCLUDED.estimated_value_numeric,
                    cycle_numeric = EXCLUDED.cycle_numeric,
                    has_pdf_url = EXCLUDED.has_pdf_url,
                    has_estimated_value = EXCLUDED.has_estimated_value,
                    is_open = EXCLUDED.is_open,
                    updated_at = CURRENT_TIMESTAMP
            """
            
            self.cursor.execute(query, record)
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error writing tender record: {e}")
            self.conn.rollback()
            return False
    
    def write_pdf(self, record: Dict[str, Any]) -> bool:
        """
        Write PDF record to etenders_pdf table
        
        Args:
            record: PDF data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract only the fields we need, handle pdf_content specially
            pdf_data = {
                'resource_id': record.get('resource_id'),
                'pdf_url': record.get('pdf_url'),
                'pdf_parsed': record.get('pdf_parsed', False),
                'pdf_content': record.get('pdf_content', '')
            }
            
            query = """
                INSERT INTO etenders_pdf (
                    resource_id, pdf_url, pdf_parsed, pdf_content
                ) VALUES (
                    %(resource_id)s, %(pdf_url)s, %(pdf_parsed)s, %(pdf_content)s
                )
                ON CONFLICT (resource_id) DO UPDATE SET
                    pdf_url = EXCLUDED.pdf_url,
                    pdf_parsed = EXCLUDED.pdf_parsed,
                    pdf_content = EXCLUDED.pdf_content,
                    updated_at = CURRENT_TIMESTAMP
            """
            
            self.cursor.execute(query, pdf_data)
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error writing PDF record: {e}")
            self.conn.rollback()
            return False
    
    def write_cpv(self, record: Dict[str, Any]) -> bool:
        """
        Write CPV record to cpv_checker table
        
        Args:
            record: CPV data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert lists/dicts to JSON for JSONB columns
            cpv_codes = Json(record.get('cpv_codes', []))
            cpv_details = Json(record.get('cpv_details', {}))
            
            query = """
                INSERT INTO cpv_checker (
                    resource_id, cpv_count, cpv_codes, cpv_details, has_validated_cpv
                ) VALUES (
                    %(resource_id)s, %(cpv_count)s, %(cpv_codes)s, %(cpv_details)s, %(has_validated_cpv)s
                )
                ON CONFLICT (resource_id) DO UPDATE SET
                    cpv_count = EXCLUDED.cpv_count,
                    cpv_codes = EXCLUDED.cpv_codes,
                    cpv_details = EXCLUDED.cpv_details,
                    has_validated_cpv = EXCLUDED.has_validated_cpv
            """
            
            params = {
                'resource_id': record.get('resource_id'),
                'cpv_count': record.get('cpv_count', 0),
                'cpv_codes': cpv_codes,
                'cpv_details': cpv_details,
                'has_validated_cpv': record.get('has_validated_cpv', False)
            }
            
            self.cursor.execute(query, params)
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error writing CPV record: {e}")
            self.conn.rollback()
            return False
    
    def write_bid_analysis(self, record: Dict[str, Any]) -> bool:
        """
        Write bid analysis to bid_analysis table
        
        Args:
            record: Bid analysis dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT INTO bid_analysis (
                    resource_id, should_bid, confidence, reasoning, 
                    relevant_factors, estimated_fit, analyzed_at
                ) VALUES (
                    %(resource_id)s, %(should_bid)s, %(confidence)s, %(reasoning)s,
                    %(relevant_factors)s, %(estimated_fit)s, %(analyzed_at)s
                )
                ON CONFLICT (resource_id) DO UPDATE SET
                    should_bid = EXCLUDED.should_bid,
                    confidence = EXCLUDED.confidence,
                    reasoning = EXCLUDED.reasoning,
                    relevant_factors = EXCLUDED.relevant_factors,
                    estimated_fit = EXCLUDED.estimated_fit,
                    analyzed_at = EXCLUDED.analyzed_at,
                    updated_at = CURRENT_TIMESTAMP
            """
            
            self.cursor.execute(query, record)
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error writing bid analysis: {e}")
            self.conn.rollback()
            return False
    
    def write_records(self, 
                     tender_records: List[Dict[str, Any]], 
                     pdf_records: List[Dict[str, Any]], 
                     cpv_records: List[Dict[str, Any]],
                     bid_records: List[Dict[str, Any]] = None) -> tuple[str, str, str, str]:
        """
        Write all records to their respective tables
        
        Args:
            tender_records: List of tender records
            pdf_records: List of PDF records
            cpv_records: List of CPV records
            bid_records: Optional list of bid analysis records
            
        Returns:
            Tuple of (tender_count, pdf_count, cpv_count, bid_count) as strings
        """
        tender_count = 0
        pdf_count = 0
        cpv_count = 0
        bid_count = 0
        
        # Write tender records
        for record in tender_records:
            if self.write_tender(record):
                tender_count += 1
        
        logger.info(f"Wrote {tender_count}/{len(tender_records)} tender records")
        
        # Write PDF records
        for record in pdf_records:
            if record:  # Skip empty records
                if self.write_pdf(record):
                    pdf_count += 1
        
        logger.info(f"Wrote {pdf_count}/{len(pdf_records)} PDF records")
        
        # Write CPV records
        for record in cpv_records:
            if record:  # Skip empty records
                if self.write_cpv(record):
                    cpv_count += 1
        
        logger.info(f"Wrote {cpv_count}/{len(cpv_records)} CPV records")
        
        # Write bid analysis records if provided
        if bid_records:
            for record in bid_records:
                if record:
                    if self.write_bid_analysis(record):
                        bid_count += 1
            
            logger.info(f"Wrote {bid_count}/{len(bid_records)} bid analysis records")
        
        return (tender_count, pdf_count, cpv_count, bid_count)
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
