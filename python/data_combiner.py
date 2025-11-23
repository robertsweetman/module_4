"""
Data combiner - joins tender, PDF, and CPV data using resource_id as key
"""

import json
import csv
from typing import Dict, Any, List, Optional


def load_json_data(tenders_file: str, pdfs_file: str, cpvs_file: str) -> List[Dict[str, Any]]:
    """
    Load and combine JSON data from three separate files.
    
    Args:
        tenders_file: Path to tenders JSON file
        pdfs_file: Path to PDFs JSON file
        cpvs_file: Path to CPVs JSON file
        
    Returns:
        List of combined records with all data joined by resource_id
    """
    # Load all files
    with open(tenders_file, 'r', encoding='utf-8') as f:
        tenders = {t['resource_id']: t for t in json.load(f)}
    
    try:
        with open(pdfs_file, 'r', encoding='utf-8') as f:
            pdfs = {p['resource_id']: p for p in json.load(f)}
    except (FileNotFoundError, json.JSONDecodeError):
        pdfs = {}
    
    try:
        with open(cpvs_file, 'r', encoding='utf-8') as f:
            cpvs = {c['resource_id']: c for c in json.load(f)}
    except (FileNotFoundError, json.JSONDecodeError):
        cpvs = {}
    
    # Combine data
    combined = []
    for resource_id, tender in tenders.items():
        record = {
            'resource_id': resource_id,
            'tender': tender,
            'pdf': pdfs.get(resource_id),
            'cpv': cpvs.get(resource_id)
        }
        combined.append(record)
    
    return combined


def load_csv_data(tenders_file: str, pdfs_file: str, cpvs_file: str) -> List[Dict[str, Any]]:
    """
    Load and combine CSV data from three separate files.
    
    Args:
        tenders_file: Path to tenders CSV file
        pdfs_file: Path to PDFs CSV file
        cpvs_file: Path to CPVs CSV file
        
    Returns:
        List of combined records with all data joined by resource_id
    """
    # Load tenders
    with open(tenders_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        tenders = {int(row['resource_id']): row for row in reader}
    
    # Load PDFs
    pdfs = {}
    try:
        with open(pdfs_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            pdfs = {int(row['resource_id']): row for row in reader}
    except FileNotFoundError:
        pass
    
    # Load CPVs
    cpvs = {}
    try:
        with open(cpvs_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            cpvs = {int(row['resource_id']): row for row in reader}
    except FileNotFoundError:
        pass
    
    # Combine data
    combined = []
    for resource_id, tender in tenders.items():
        record = {
            'resource_id': resource_id,
            'tender': tender,
            'pdf': pdfs.get(resource_id),
            'cpv': cpvs.get(resource_id)
        }
        combined.append(record)
    
    return combined


def load_postgres_data(connection_string: str) -> List[Dict[str, Any]]:
    """
    Load and combine data from PostgreSQL tables.
    
    Args:
        connection_string: PostgreSQL connection string
        
    Returns:
        List of combined records with all data joined by resource_id
    """
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Query with LEFT JOINs to get all data
    query = """
        SELECT 
            t.*,
            row_to_json(p.*) as pdf_data,
            row_to_json(c.*) as cpv_data
        FROM tenders t
        LEFT JOIN pdfs p ON t.resource_id = p.resource_id
        LEFT JOIN cpvs c ON t.resource_id = c.resource_id
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    combined = []
    for row in rows:
        record = {
            'resource_id': row['resource_id'],
            'tender': dict(row),
            'pdf': row.get('pdf_data'),
            'cpv': row.get('cpv_data')
        }
        combined.append(record)
    
    cursor.close()
    conn.close()
    
    return combined


def combine_data(source_type: str, **kwargs) -> List[Dict[str, Any]]:
    """
    Combine tender, PDF, and CPV data from any source type.
    
    Args:
        source_type: 'json', 'csv', or 'postgres'
        **kwargs: Source-specific arguments (file paths or connection string)
        
    Returns:
        List of combined records
    """
    if source_type == 'json':
        return load_json_data(
            kwargs['tenders_file'],
            kwargs['pdfs_file'],
            kwargs['cpvs_file']
        )
    elif source_type == 'csv':
        return load_csv_data(
            kwargs['tenders_file'],
            kwargs['pdfs_file'],
            kwargs['cpvs_file']
        )
    elif source_type == 'postgres':
        return load_postgres_data(kwargs['connection_string'])
    else:
        raise ValueError(f"Unknown source type: {source_type}")


if __name__ == "__main__":
    # Test with CSV files
    import glob
    
    # Find most recent files
    tender_files = sorted(glob.glob('outputs/csv/tenders_*.csv'), reverse=True)
    pdf_files = sorted(glob.glob('outputs/csv/pdfs_*.csv'), reverse=True)
    cpv_files = sorted(glob.glob('outputs/csv/cpvs_*.csv'), reverse=True)
    
    if tender_files:
        combined = combine_data(
            'csv',
            tenders_file=tender_files[0],
            pdfs_file=pdf_files[0] if pdf_files else 'pdfs.csv',
            cpvs_file=cpv_files[0] if cpv_files else 'cpvs.csv'
        )
        
        print(f"Combined {len(combined)} records")
        if combined:
            print(f"\nSample record structure:")
            print(json.dumps(combined[0], indent=2, default=str))
    else:
        print("No tender files found")
