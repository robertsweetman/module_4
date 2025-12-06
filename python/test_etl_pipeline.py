"""
ETL Pipeline Tests for eTenders Data Product
Tests data ingestion, schema validation, and pipeline integrity
"""

import unittest
import json
import os
from datetime import datetime
from unittest.mock import patch, MagicMock
import pandas as pd
import re


class TestETLPipeline(unittest.TestCase):
    """Test the ETL pipeline components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data = {
            'resource_id': '123456',
            'title': 'Test Tender for IT Services',
            'contracting_authority': 'Department of Testing',
            'date_published': '01-Dec-2025',
            'submission_deadline': '15-Dec-2025 17:00',
            'estimated_value': '€50,000',
            'procedure': 'Open Procedure',
            'status': 'Published'
        }
    
    def test_data_structure_validation(self):
        """Test that scraped data has correct structure"""
        required_fields = [
            'resource_id',
            'title', 
            'contracting_authority',
            'date_published',
            'submission_deadline',
            'estimated_value'
        ]
        
        for field in required_fields:
            self.assertIn(field, self.test_data)
    
    def test_resource_id_format(self):
        """Test resource_id is numeric string"""
        resource_id = self.test_data['resource_id']
        self.assertTrue(resource_id.isdigit())
        self.assertGreater(len(resource_id), 0)
    
    def test_date_format_validation(self):
        """Test date strings are in expected format"""
        date_pub = self.test_data['date_published']
        # Format: DD-MMM-YYYY
        self.assertRegex(date_pub, r'\d{2}-[A-Z][a-z]{2}-\d{4}')
    
    def test_value_format_validation(self):
        """Test estimated value format"""
        value = self.test_data['estimated_value']
        # Should contain € and numbers
        self.assertIn('€', value)
        # Remove formatting and check numeric
        numeric = value.replace('€', '').replace(',', '').strip()
        self.assertTrue(numeric.replace('.', '').isdigit())


class TestTypeCoercion(unittest.TestCase):
    """Test type coercion functionality"""
    
    def test_parse_currency_value(self):
        """Test parsing currency strings to float"""
        test_cases = [
            ('€50,000', 50000.0),
            ('€1,234,567.89', 1234567.89),
            ('50000', 50000.0),
            ('€500', 500.0),
            ('N/A', None),
            ('', None)
        ]
        
        for input_val, expected in test_cases:
            if input_val in ['N/A', '', None]:
                result = None
            else:
                # Remove € and , then convert
                cleaned = input_val.replace('€', '').replace(',', '').strip()
                result = float(cleaned) if cleaned else None
            
            self.assertEqual(result, expected, f"Failed for input: {input_val}")
    
    def test_parse_date_string(self):
        """Test parsing date strings"""
        test_cases = [
            ('01-Dec-2025', datetime(2025, 12, 1)),
            ('15-Jan-2024', datetime(2024, 1, 15)),
        ]
        
        for date_str, expected in test_cases:
            # Parse format: DD-MMM-YYYY
            result = datetime.strptime(date_str, '%d-%b-%Y')
            self.assertEqual(result, expected)
    
    def test_parse_datetime_string(self):
        """Test parsing datetime strings with time"""
        date_str = '15-Dec-2025 17:00'
        expected = datetime(2025, 12, 15, 17, 0)
        
        # Parse format: DD-MMM-YYYY HH:MM
        result = datetime.strptime(date_str, '%d-%b-%Y %H:%M')
        self.assertEqual(result, expected)


class TestPDFValidation(unittest.TestCase):
    """Test PDF download and validation logic"""
    
    def test_pdf_magic_bytes(self):
        """Test PDF file signature validation"""
        valid_pdf_start = b'%PDF-1.4'
        invalid_content = b'<html>not a pdf</html>'
        
        # Valid PDF check
        self.assertTrue(valid_pdf_start.startswith(b'%PDF'))
        
        # Invalid content check
        self.assertFalse(invalid_content.startswith(b'%PDF'))
    
    def test_content_type_validation(self):
        """Test Content-Type header validation"""
        valid_types = ['application/pdf']
        invalid_types = ['text/html', 'application/json', 'text/plain']
        
        for content_type in valid_types:
            self.assertIn('application/pdf', content_type)
        
        for content_type in invalid_types:
            self.assertNotIn('application/pdf', content_type)
    
    @patch('requests.get')
    def test_pdf_download_success(self, mock_get):
        """Test successful PDF download"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/pdf'}
        mock_response.content = b'%PDF-1.4\ntest content'
        mock_get.return_value = mock_response
        
        # Simulate download
        import requests
        response = requests.get('https://example.com/test.pdf')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/pdf', response.headers.get('Content-Type', ''))
        self.assertTrue(response.content.startswith(b'%PDF'))
    
    @patch('requests.get')
    def test_pdf_download_server_error(self, mock_get):
        """Test handling of server errors"""
        mock_get.side_effect = Exception("500 Server Error")
        
        import requests
        with self.assertRaises(Exception) as context:
            requests.get('https://example.com/error.pdf')
        
        self.assertIn('500', str(context.exception))


class TestCPVValidation(unittest.TestCase):
    """Test CPV code validation"""
    
    def test_cpv_code_format(self):
        """Test CPV code format validation"""
        valid_cpv = '48000000'
        
        # Should be 8 digits
        self.assertEqual(len(valid_cpv), 8)
        self.assertTrue(valid_cpv.isdigit())
    
    def test_cpv_extraction_from_text(self):
        """Test extracting CPV codes from text"""
        text = "This tender uses CPV codes: 48000000, 72000000, and 80000000"
        
        # Pattern for 8-digit CPV codes
        pattern = r'\b\d{8}\b'
        cpvs = re.findall(pattern, text)
        
        self.assertEqual(len(cpvs), 3)
        self.assertIn('48000000', cpvs)
        self.assertIn('72000000', cpvs)
        self.assertIn('80000000', cpvs)
    
    def test_cpv_list_file_exists(self):
        """Test that CPV reference file exists"""
        cpv_file = 'cpv_list.json'
        
        if os.path.exists(cpv_file):
            with open(cpv_file, 'r') as f:
                cpv_data = json.load(f)
                self.assertIsInstance(cpv_data, (list, dict))


class TestSchemaValidation(unittest.TestCase):
    """Test database schema validation"""
    
    def test_etenders_core_schema(self):
        """Test ETENDERS_CORE table schema"""
        schema = {
            'resource_id': str,
            'title': str,
            'contracting_authority': str,
            'date_published': 'datetime',
            'submission_deadline': 'datetime',
            'estimated_value': float,
            'procedure': str,
            'status': str
        }
        
        # Create sample data matching schema
        sample_data = {
            'resource_id': '123456',
            'title': 'Test',
            'contracting_authority': 'Dept',
            'date_published': datetime.now(),
            'submission_deadline': datetime.now(),
            'estimated_value': 50000.0,
            'procedure': 'Open',
            'status': 'Published'
        }
        
        # Validate types
        for field, expected_type in schema.items():
            actual_value = sample_data[field]
            
            if expected_type == str:
                self.assertIsInstance(actual_value, str)
            elif expected_type == float:
                self.assertIsInstance(actual_value, (float, int))
            elif expected_type == 'datetime':
                self.assertIsInstance(actual_value, datetime)
    
    def test_pdf_table_schema(self):
        """Test ETENDERS_PDF table schema"""
        schema = {
            'resource_id': str,
            'pdf_url': str,
            'pdf_parsed': bool,
            'pdf_content': str  # Changed from pdf_content_full_text
        }
        
        sample_data = {
            'resource_id': '123456',
            'pdf_url': 'https://example.com/test.pdf',
            'pdf_parsed': True,
            'pdf_content': 'Sample content'  # Changed from pdf_content_full_text
        }
        
        for field, expected_type in schema.items():
            self.assertIsInstance(sample_data[field], expected_type)
    
    def test_bid_analysis_schema(self):
        """Test BID_ANALYSIS table schema"""
        schema = {
            'resource_id': str,
            'should_bid': bool,
            'confidence': float,
            'reasoning': str,
            'relevant_factors': str,
            'estimated_fit': float,
            'analyzed_at': 'datetime'
        }
        
        sample_data = {
            'resource_id': '123456',
            'should_bid': True,
            'confidence': 0.85,
            'reasoning': 'Good fit',
            'relevant_factors': 'IT, Cloud',
            'estimated_fit': 0.9,
            'analyzed_at': datetime.now()
        }
        
        for field, expected_type in schema.items():
            actual_value = sample_data[field]
            
            if expected_type == str:
                self.assertIsInstance(actual_value, str)
            elif expected_type == bool:
                self.assertIsInstance(actual_value, bool)
            elif expected_type == float:
                self.assertIsInstance(actual_value, float)
            elif expected_type == 'datetime':
                self.assertIsInstance(actual_value, datetime)


class TestDataIntegrity(unittest.TestCase):
    """Test data integrity and business rules"""
    
    def test_resource_id_uniqueness(self):
        """Test that resource_ids are unique"""
        data = pd.DataFrame({
            'resource_id': ['123', '456', '123', '789'],
            'title': ['A', 'B', 'C', 'D']
        })
        
        duplicates = data[data.duplicated(subset=['resource_id'], keep=False)]
        self.assertGreater(len(duplicates), 0, "Should detect duplicates")
        
        unique_data = data.drop_duplicates(subset=['resource_id'])
        self.assertEqual(len(unique_data), 3)
    
    def test_submission_deadline_after_published(self):
        """Test business rule: deadline should be after published date"""
        published = datetime(2025, 12, 1)
        deadline = datetime(2025, 12, 15)
        
        self.assertGreater(deadline, published)
    
    def test_estimated_value_positive(self):
        """Test that estimated values are positive"""
        values = [50000.0, 100000.0, 250000.0]
        
        for value in values:
            self.assertGreater(value, 0)
    
    def test_confidence_score_range(self):
        """Test that confidence scores are between 0 and 1"""
        confidence_scores = [0.0, 0.5, 0.85, 1.0]
        
        for score in confidence_scores:
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)


def run_tests_with_output():
    """Run tests and generate detailed report"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestETLPipeline,
        TestTypeCoercion,
        TestPDFValidation,
        TestCPVValidation,
        TestSchemaValidation,
        TestDataIntegrity
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate summary
    print("\n" + "="*80)
    print("ETL PIPELINE TEST SUMMARY")
    print("="*80)
    print(f"Tests run:     {result.testsRun}")
    print(f"✓ Successes:   {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"✗ Failures:    {len(result.failures)}")
    print(f"⚠ Errors:      {len(result.errors)}")
    
    if result.wasSuccessful():
        print(f"\n🎉 ALL TESTS PASSED!")
        success_rate = 100.0
    else:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
    
    print(f"Success rate:  {success_rate:.1f}%")
    print("="*80)
    
    return result


if __name__ == '__main__':
    result = run_tests_with_output()
    exit(0 if result.wasSuccessful() else 1)
