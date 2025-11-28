"""
PostgreSQL output handler with error logging
"""

import logging
import psycopg2
from psycopg2.extras import Json
from typing import Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


class PostgresOutput:
    def __init__(self, 
                 table_name: str = 'tenders',
                 log_file: str = 'postgres_output_errors.log',
                 connection_string: str = None):
        """
        Initialize PostgreSQL output handler.
        
        Args:
            table_name: Name of the table to insert records
            log_file: Path to error log file
            connection_string: PostgreSQL connection string (or from env var)
        """
        self.table_name = table_name
        self.log_file = log_file
        self.connection_string = connection_string or os.environ.get('DATABASE_URL')
        self.conn = None
        self.cursor = None
        self.records_written = 0
        self.error_count = 0
        
    def connect(self) -> bool:
        """
        Establish database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if not self.connection_string:
                logger.error("No database connection string provided")
                raise ValueError("No database connection string provided")
            
            logger.info(f"Connecting to PostgreSQL database for table: {self.table_name}")
            self.conn = psycopg2.connect(self.connection_string)
            self.cursor = self.conn.cursor()
            logger.info(f"Successfully connected to PostgreSQL database")
            print(f"✓ Connected to PostgreSQL database")
            return True
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}", exc_info=True)
            print(f"✗ Database connection failed: {e}")
            self._log_error({'action': 'connect'}, str(e))
            return False
    
    def write_record(self, record: Dict[str, Any]) -> bool:
        """
        Write a single record to database.
        
        Args:
            record: Dictionary to insert
            
        Returns:
            True if successful, False otherwise
        """
        if not self.cursor:
            if not self.connect():
                return False
        
        try:
            # Build dynamic INSERT statement
            columns = list(record.keys())
            placeholders = [f"%({col})s" for col in columns]
            
            # Convert dict/list fields to JSON
            record_json = {}
            for key, value in record.items():
                if isinstance(value, (dict, list)):
                    record_json[key] = Json(value)
                else:
                    record_json[key] = value
            
            query = f"""
                INSERT INTO {self.table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                ON CONFLICT (resource_id) DO UPDATE SET
                {', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'resource_id'])}
            """
            
            self.cursor.execute(query, record_json)
            self.records_written += 1
            logger.debug(f"Wrote record to {self.table_name}: {record.get('resource_id')}")
            
            return True
            
        except psycopg2.IntegrityError as e:
            self.error_count += 1
            logger.warning(f"Duplicate record in {self.table_name}: {record.get('resource_id')}")
            self._log_error(record, str(e))
            if self.conn:
                self.conn.rollback()
            return False
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error writing record to {self.table_name}: {e}", exc_info=True)
            self._log_error(record, str(e))
            # Rollback the failed transaction
            if self.conn:
                self.conn.rollback()
            return False
    
    def flush(self) -> None:
        """Commit all pending transactions."""
        if self.conn:
            try:
                self.conn.commit()
                logger.info(f"Committed {self.records_written} records to {self.table_name}")
                print(f"✓ Committed {self.records_written} records to {self.table_name}")
            except Exception as e:
                logger.error(f"Error committing to database: {e}", exc_info=True)
                print(f"✗ Error committing to database: {e}")
                self._log_error({'action': 'flush'}, str(e))
                self.conn.rollback()
    
    def close(self) -> None:
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info(f"Database connection closed for {self.table_name}")
        print(f"✓ Database connection closed")
    
    def _log_error(self, record: Dict[str, Any], error: str) -> None:
        """Log errors to file."""
        timestamp = datetime.now().isoformat()
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] PostgreSQL Write Error\n")
            f.write(f"Error: {error}\n")
            f.write(f"Record ID: {record.get('resource_id', 'unknown')}\n")
            f.write(f"Record: {str(record)[:500]}...\n")
            f.write("-" * 80 + "\n")
    
    def get_stats(self) -> Dict[str, int]:
        """Get output statistics."""
        return {
            'records_written': self.records_written,
            'errors': self.error_count
        }
    
    def create_table(self) -> bool:
        """
        Create the appropriate table based on table_name.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.cursor:
            if not self.connect():
                return False
        
        try:
            if self.table_name == 'tenders':
                create_table_sql = """
                    CREATE TABLE IF NOT EXISTS tenders (
                        resource_id INTEGER PRIMARY KEY,
                        row_number TEXT,
                        title TEXT,
                        detail_url TEXT,
                        contracting_authority TEXT,
                        info TEXT,
                        date_published TEXT,
                        date_published_parsed TEXT,
                        submission_deadline TEXT,
                        submission_deadline_parsed TEXT,
                        procedure TEXT,
                        status TEXT,
                        notice_pdf_url TEXT,
                        award_date TEXT,
                        award_date_parsed TEXT,
                        estimated_value TEXT,
                        estimated_value_numeric NUMERIC,
                        cycle TEXT,
                        cycle_numeric INTEGER,
                        has_pdf_url BOOLEAN,
                        has_estimated_value BOOLEAN,
                        is_open BOOLEAN,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_tenders_resource_id ON tenders(resource_id);
                    CREATE INDEX IF NOT EXISTS idx_tenders_status ON tenders(status);
                """
            elif self.table_name == 'pdfs':
                create_table_sql = """
                    CREATE TABLE IF NOT EXISTS pdfs (
                        resource_id INTEGER PRIMARY KEY,
                        pdf_url TEXT,
                        pdf_parsed BOOLEAN,
                        procedure_id TEXT,
                        title TEXT,
                        buyer_name TEXT,
                        buyer_country TEXT,
                        estimated_value TEXT,
                        start_date TEXT,
                        duration_months TEXT,
                        submission_deadline TEXT,
                        main_classification TEXT,
                        lots JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (resource_id) REFERENCES tenders(resource_id) ON DELETE CASCADE
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_pdfs_resource_id ON pdfs(resource_id);
                    CREATE INDEX IF NOT EXISTS idx_pdfs_buyer_name ON pdfs(buyer_name);
                """
            elif self.table_name == 'cpvs':
                create_table_sql = """
                    CREATE TABLE IF NOT EXISTS cpvs (
                        resource_id INTEGER PRIMARY KEY,
                        cpv_count INTEGER,
                        cpv_codes TEXT[],
                        cpv_details JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (resource_id) REFERENCES tenders(resource_id) ON DELETE CASCADE
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_cpvs_resource_id ON cpvs(resource_id);
                    CREATE INDEX IF NOT EXISTS idx_cpvs_codes ON cpvs USING GIN(cpv_codes);
                    CREATE INDEX IF NOT EXISTS idx_cpvs_details ON cpvs USING GIN(cpv_details);
                """
            else:
                raise ValueError(f"Unknown table name: {self.table_name}")
            
            logger.info(f"Creating/verifying table: {self.table_name}")
            self.cursor.execute(create_table_sql)
            self.conn.commit()
            logger.info(f"Table {self.table_name} is ready")
            print(f"✓ Table {self.table_name} ready")
            return True
            
        except Exception as e:
            logger.error(f"Error creating table {self.table_name}: {e}", exc_info=True)
            print(f"✗ Error creating table: {e}")
            self._log_error({'action': 'create_table'}, str(e))
            return False


if __name__ == "__main__":
    # Test PostgreSQL output (requires DATABASE_URL in .env)
    print("Testing PostgreSQL output...")
    print("Set DATABASE_URL in .env to test")
    
    # Example:
    # output = PostgresOutput()
    # output.create_table()
    # output.write_record({'resource_id': 1, 'title': 'Test'})
    # output.flush()
    # output.close()
