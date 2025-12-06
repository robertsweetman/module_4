"""
Simple test runner for eTenders ETL Pipeline
Executes all pipeline tests and generates summary report
"""

import sys
import os

# Ensure current directory is in path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == '__main__':
    from test_etl_pipeline import run_tests_with_output
    result = run_tests_with_output()
    sys.exit(0 if result.wasSuccessful() else 1)
