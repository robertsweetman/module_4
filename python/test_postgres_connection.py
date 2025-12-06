"""
Test PostgreSQL connection and insert sample data
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from datetime import datetime

# Load environment variables
load_dotenv()

def test_connection():
    """Test database connection"""
    print("🔌 Testing PostgreSQL connection...")
    
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'etenders_db'),
        'user': os.getenv('DB_USER', 'etenders_user'),
        'password': os.getenv('DB_PASSWORD', 'etenders_pass')
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✓ Connected successfully!")
        print(f"  PostgreSQL version: {version.split(',')[0]}")
        
        # List tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print(f"\n📊 Tables in database ({len(tables)}):")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
            count = cursor.fetchone()[0]
            print(f"  • {table[0]}: {count} records")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def insert_sample_data():
    """Insert sample tender data"""
    print("\n📝 Inserting sample data...")
    
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'etenders_db'),
        'user': os.getenv('DB_USER', 'etenders_user'),
        'password': os.getenv('DB_PASSWORD', 'etenders_pass')
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Sample tender
        cursor.execute("""
            INSERT INTO etenders_core (
                resource_id, title, contracting_authority, 
                date_published, submission_deadline, 
                estimated_value, status, is_open
            ) VALUES (
                'TEST001', 
                'Sample IT Services Tender', 
                'Department of Example',
                CURRENT_DATE,
                CURRENT_DATE + INTERVAL '30 days',
                50000.00,
                'Published',
                TRUE
            ) ON CONFLICT (resource_id) DO UPDATE SET
                title = EXCLUDED.title,
                updated_at = CURRENT_TIMESTAMP;
        """)
        
        # Sample PDF record
        cursor.execute("""
            INSERT INTO etenders_pdf (
                resource_id, pdf_url, pdf_parsed, pdf_content_full_text
            ) VALUES (
                'TEST001',
                'https://example.com/test.pdf',
                TRUE,
                'Sample PDF content for testing purposes'
            ) ON CONFLICT (resource_id) DO UPDATE SET
                pdf_content_full_text = EXCLUDED.pdf_content_full_text;
        """)
        
        # Sample bid analysis
        cursor.execute("""
            INSERT INTO bid_analysis (
                resource_id, should_bid, confidence, 
                reasoning, estimated_fit
            ) VALUES (
                'TEST001',
                TRUE,
                0.85,
                'Good fit for our capabilities in IT services',
                0.90
            ) ON CONFLICT (resource_id) DO UPDATE SET
                confidence = EXCLUDED.confidence;
        """)
        
        # Sample CPV checker
        cursor.execute("""
            INSERT INTO cpv_checker (
                resource_id, cpv_count, cpv_codes, has_validated_cpv
            ) VALUES (
                'TEST001',
                2,
                '48000000, 72000000',
                TRUE
            ) ON CONFLICT (resource_id) DO UPDATE SET
                cpv_count = EXCLUDED.cpv_count;
        """)
        
        # Sample sales update
        cursor.execute("""
            INSERT INTO sales_updates (
                resource_id, date, sales_comment, author
            ) VALUES (
                'TEST001',
                CURRENT_DATE,
                'Initial review - looks promising',
                'Test User'
            );
        """)
        
        conn.commit()
        print("✓ Sample data inserted successfully")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM etenders_core;")
        count = cursor.fetchone()[0]
        print(f"  Total tenders in database: {count}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Failed to insert sample data: {e}")
        return False


def query_sample_data():
    """Query and display sample data"""
    print("\n🔍 Querying data...")
    
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'etenders_db'),
        'user': os.getenv('DB_USER', 'etenders_user'),
        'password': os.getenv('DB_PASSWORD', 'etenders_pass')
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Query with joins
        cursor.execute("""
            SELECT 
                ec.resource_id,
                ec.title,
                ec.estimated_value,
                ba.should_bid,
                ba.confidence,
                cpv.cpv_count
            FROM etenders_core ec
            LEFT JOIN bid_analysis ba ON ec.resource_id = ba.resource_id
            LEFT JOIN cpv_checker cpv ON ec.resource_id = cpv.resource_id
            LIMIT 5;
        """)
        
        rows = cursor.fetchall()
        
        if rows:
            print("\nSample tender data:")
            print("-" * 100)
            print(f"{'ID':<10} {'Title':<40} {'Value':<12} {'Bid?':<8} {'Conf.':<8} {'CPVs':<6}")
            print("-" * 100)
            
            for row in rows:
                resource_id, title, value, should_bid, confidence, cpv_count = row
                title_short = (title[:37] + '...') if len(title) > 40 else title
                value_str = f"€{value:,.2f}" if value else "N/A"
                bid_str = "Yes" if should_bid else "No" if should_bid is False else "N/A"
                conf_str = f"{confidence:.2f}" if confidence else "N/A"
                cpv_str = str(cpv_count) if cpv_count else "0"
                
                print(f"{resource_id:<10} {title_short:<40} {value_str:<12} {bid_str:<8} {conf_str:<8} {cpv_str:<6}")
            
            print("-" * 100)
        else:
            print("No data found")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Query failed: {e}")
        return False


def cleanup_sample_data():
    """Remove all sample test data"""
    print("\n🧹 Cleaning up sample data...")
    
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'etenders_db'),
        'user': os.getenv('DB_USER', 'etenders_user'),
        'password': os.getenv('DB_PASSWORD', 'etenders_pass')
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Delete sample data (cascades to related tables)
        cursor.execute("DELETE FROM etenders_core WHERE resource_id = 'TEST001';")
        
        conn.commit()
        print("✓ Sample data removed")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Failed to cleanup: {e}")
        return False


if __name__ == '__main__':
    print("=" * 50)
    print("eTenders PostgreSQL Test")
    print("=" * 50)
    
    if test_connection():
        # Only show data if it exists
        query_sample_data()
        print("\n✅ Connection test passed!")
        print("\nOptional commands:")
        print("  python3 test_postgres_connection.py --insert   # Add temporary test data")
        print("  python3 test_postgres_connection.py --cleanup  # Remove test data")
    else:
        print("\n❌ Connection test failed")
        print("\nMake sure PostgreSQL is running:")
        print("  docker start etenders-postgres")
        sys.exit(1)
    
    # Handle optional operations
    if '--insert' in sys.argv or '--sample' in sys.argv:
        insert_sample_data()
        query_sample_data()
        print("\n⚠️  Sample data inserted. Run with --cleanup to remove it.")
    
    if '--cleanup' in sys.argv:
        cleanup_sample_data()
        query_sample_data()
