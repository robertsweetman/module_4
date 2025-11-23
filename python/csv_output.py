"""
CSV output handler with error logging
"""

import csv
from typing import Dict, Any, List
from datetime import datetime


class CSVOutput:
    def __init__(self, output_file: str = 'output.csv', log_file: str = 'csv_output_errors.log', streaming: bool = True):
        """
        Initialize CSV output handler.
        
        Args:
            output_file: Path to output CSV file
            log_file: Path to error log file
            streaming: If True, write records immediately; if False, buffer in memory
        """
        self.output_file = output_file
        self.log_file = log_file
        self.streaming = streaming
        self.records = [] if not streaming else None
        self.error_count = 0
        self.records_written = 0
        self.fieldnames = None
        self.file_handle = None
        self.csv_writer = None
        
        if streaming:
            # Open file for streaming writes
            self.file_handle = open(output_file, 'w', newline='', encoding='utf-8')
        
    def write_record(self, record: Dict[str, Any]) -> bool:
        """
        Write a single record to the buffer or file.
        
        Args:
            record: Dictionary to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Flatten nested structures for CSV
            flat_record = self._flatten_record(record)
            
            # Update fieldnames
            if self.fieldnames is None:
                self.fieldnames = list(flat_record.keys())
                if self.streaming:
                    # Write header on first record
                    self.csv_writer = csv.DictWriter(self.file_handle, fieldnames=self.fieldnames, extrasaction='ignore')
                    self.csv_writer.writeheader()
            else:
                # Add any new fields
                new_fields = [key for key in flat_record.keys() if key not in self.fieldnames]
                if new_fields:
                    self.fieldnames.extend(new_fields)
                    if self.streaming:
                        # Can't add fields mid-stream in CSV, log warning
                        print(f"⚠ Warning: New fields found mid-stream: {new_fields}")
            
            if self.streaming:
                # Write directly to file
                row = {field: flat_record.get(field, '') for field in self.fieldnames}
                self.csv_writer.writerow(row)
                self.records_written += 1
            else:
                # Buffer in memory
                self.records.append(flat_record)
                self.records_written += 1
            
            return True
            
        except Exception as e:
            self.error_count += 1
            self._log_error(record, str(e))
            return False
    
    def flush(self) -> None:
        """Write all buffered records to CSV file or close streaming file."""
        if self.streaming:
            # Just close the file handle
            if self.file_handle:
                self.file_handle.close()
                self.file_handle = None
            print(f"✓ Wrote {self.records_written} records to {self.output_file}")
        else:
            # Write all buffered records
            if not self.records:
                print("⚠ No records to write to CSV")
                return
                
            try:
                with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.fieldnames, extrasaction='ignore')
                    writer.writeheader()
                    
                    for record in self.records:
                        # Ensure all fields exist
                        row = {field: record.get(field, '') for field in self.fieldnames}
                        writer.writerow(row)
                
                print(f"✓ Wrote {len(self.records)} records to {self.output_file}")
                
            except Exception as e:
                print(f"✗ Error writing CSV file: {e}")
                self._log_error({'action': 'flush'}, str(e))
    
    def _flatten_record(self, record: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """
        Flatten nested dictionary for CSV output.
        
        Args:
            record: Dictionary to flatten
            parent_key: Parent key for nested items
            sep: Separator for nested keys
            
        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in record.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_record(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert lists to JSON strings for CSV
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    def _log_error(self, record: Dict[str, Any], error: str) -> None:
        """Log errors to file."""
        timestamp = datetime.now().isoformat()
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] CSV Write Error\n")
            f.write(f"Error: {error}\n")
            f.write(f"Record ID: {record.get('resource_id', 'unknown')}\n")
            f.write(f"Record: {str(record)[:500]}...\n")
            f.write("-" * 80 + "\n")
    
    def get_stats(self) -> Dict[str, int]:
        """Get output statistics."""
        return {
            'records_written': self.records_written if self.streaming else len(self.records),
            'errors': self.error_count,
            'fields': len(self.fieldnames) if self.fieldnames else 0
        }


def write_to_csv(records: List[Dict[str, Any]], output_file: str = 'output.csv') -> None:
    """
    Convenience function to write records to CSV.
    
    Args:
        records: List of record dictionaries
        output_file: Path to output file
    """
    output = CSVOutput(output_file)
    for record in records:
        output.write_record(record)
    output.flush()
    
    stats = output.get_stats()
    if stats['errors'] > 0:
        print(f"⚠ {stats['errors']} errors logged to csv_output_errors.log")


if __name__ == "__main__":
    # Test CSV output
    test_records = [
        {'id': 1, 'name': 'Test 1', 'value': 100, 'meta': {'color': 'red'}},
        {'id': 2, 'name': 'Test 2', 'value': 200, 'tags': ['a', 'b']}
    ]
    
    output = CSVOutput('test_output.csv')
    for record in test_records:
        output.write_record(record)
    output.flush()
    
    print(f"Stats: {output.get_stats()}")
