"""
JSON output handler with error logging
"""

import json
from typing import Dict, Any, List
from datetime import datetime
import os


class JSONOutput:
    def __init__(self, output_file: str = 'output.json', log_file: str = 'json_output_errors.log', streaming: bool = True):
        """
        Initialize JSON output handler.
        
        Args:
            output_file: Path to output JSON file
            log_file: Path to error log file
            streaming: If True, write records immediately; if False, buffer in memory
        """
        self.output_file = output_file
        self.log_file = log_file
        self.streaming = streaming
        self.records = [] if not streaming else None
        self.error_count = 0
        self.records_written = 0
        self.file_handle = None
        
        if streaming:
            # Open file and write opening bracket
            self.file_handle = open(output_file, 'w', encoding='utf-8')
            self.file_handle.write('[\n')
        
    def write_record(self, record: Dict[str, Any]) -> bool:
        """
        Write a single record to the buffer or file.
        
        Args:
            record: Dictionary to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Test JSON serialization
            json_str = json.dumps(record, default=str)
            
            if self.streaming:
                # Write directly to file
                if self.records_written > 0:
                    self.file_handle.write(',\n')
                self.file_handle.write('  ' + json_str)
                self.records_written += 1
            else:
                # Buffer in memory
                self.records.append(record)
                self.records_written += 1
            
            return True
            
        except (TypeError, ValueError) as e:
            self.error_count += 1
            self._log_error(record, str(e))
            return False
    
    def flush(self) -> None:
        """Write all buffered records to file."""
        if self.streaming:
            # Close the JSON array and file
            if self.file_handle:
                self.file_handle.write('\n]\n')
                self.file_handle.close()
                self.file_handle = None
            print(f"✓ Wrote {self.records_written} records to {self.output_file}")
        else:
            # Write all buffered records
            try:
                with open(self.output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.records, f, indent=2, default=str)
                print(f"✓ Wrote {len(self.records)} records to {self.output_file}")
                
            except Exception as e:
                print(f"✗ Error writing JSON file: {e}")
                self._log_error({'action': 'flush'}, str(e))
    
    def _log_error(self, record: Dict[str, Any], error: str) -> None:
        """Log errors to file."""
        timestamp = datetime.now().isoformat()
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] JSON Serialization Error\n")
            f.write(f"Error: {error}\n")
            f.write(f"Record ID: {record.get('resource_id', 'unknown')}\n")
            f.write(f"Record: {str(record)[:500]}...\n")
            f.write("-" * 80 + "\n")
    
    def get_stats(self) -> Dict[str, int]:
        """Get output statistics."""
        return {
            'records_written': self.records_written if self.streaming else len(self.records),
            'errors': self.error_count
        }


def write_to_json(records: List[Dict[str, Any]], output_file: str = 'output.json') -> None:
    """
    Convenience function to write records to JSON.
    
    Args:
        records: List of record dictionaries
        output_file: Path to output file
    """
    output = JSONOutput(output_file)
    for record in records:
        output.write_record(record)
    output.flush()
    
    stats = output.get_stats()
    if stats['errors'] > 0:
        print(f"⚠ {stats['errors']} errors logged to json_output_errors.log")


if __name__ == "__main__":
    # Test JSON output
    test_records = [
        {'id': 1, 'name': 'Test 1', 'value': 100},
        {'id': 2, 'name': 'Test 2', 'value': 200}
    ]
    
    output = JSONOutput('test_output.json')
    for record in test_records:
        output.write_record(record)
    output.flush()
    
    print(f"Stats: {output.get_stats()}")
