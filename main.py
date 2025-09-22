"""
Main application entry point for data cleaning operations.
"""
import sys
import os
from typing import Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.logger import logger
from src.database.connection import db_connection
from src.services.order_service import OrderService


def main():
    """Main application function."""
    logger.info("Starting data cleaning application")
    
    try:
        # Test database connection
        if not db_connection.test_connection():
            logger.error("Failed to connect to database. Please check your configuration.")
            return
        
        logger.info("Database connection successful")
        
        # Initialize order service
        order_service = OrderService()
        
        # Generate data quality report
        logger.info("Generating data quality report...")
        quality_report = order_service.get_data_quality_report()
        
        print("\n" + "="*50)
        print("DATA QUALITY REPORT")
        print("="*50)
        print(f"Total Records: {quality_report['total_records']}")
        print(f"Total Columns: {quality_report['total_columns']}")
        print(f"Duplicate Records: {quality_report['duplicate_records']}")
        
        if quality_report['null_values']:
            print("\nNull Values by Column:")
            for column, count in quality_report['null_values'].items():
                if count > 0:
                    print(f"  {column}: {count}")
        
        if quality_report['data_completeness']:
            print("\nData Completeness by Column:")
            for column, percentage in quality_report['data_completeness'].items():
                print(f"  {column}: {percentage}%")
        
        if quality_report['value_distributions']:
            print("\nValue Distributions:")
            for field, distribution in quality_report['value_distributions'].items():
                print(f"  {field}:")
                for value, count in list(distribution.items())[:5]:  # Show top 5
                    print(f"    {value}: {count}")
        
        print("\n" + "="*50)
        
        # Perform data cleaning operations
        logger.info("Starting data cleaning operations...")
        
        # Clean duplicates
        logger.info("Checking for duplicate orders...")
        duplicate_result = order_service.clean_duplicate_orders()
        print(f"\nDuplicate Cleaning Results:")
        print(f"  Total Records: {duplicate_result.total_records}")
        print(f"  Duplicates Found: {duplicate_result.cleaned_records}")
        print(f"  Warnings: {duplicate_result.warnings}")
        
        # Clean incomplete records
        logger.info("Checking for incomplete records...")
        incomplete_result = order_service.clean_incomplete_records()
        print(f"\nIncomplete Records Cleaning Results:")
        print(f"  Total Records: {incomplete_result.total_records}")
        print(f"  Incomplete Records Found: {incomplete_result.cleaned_records}")
        print(f"  Errors: {incomplete_result.errors}")
        print(f"  Warnings: {incomplete_result.warnings}")
        
        if incomplete_result.cleaning_summary.get('problematic_order_ids'):
            print(f"  Sample Problematic Order IDs: {incomplete_result.cleaning_summary['problematic_order_ids'][:10]}")
        
        # Validate data types
        logger.info("Validating data types...")
        validation_result = order_service.validate_data_types()
        print(f"\nData Type Validation Results:")
        print(f"  Total Records: {validation_result.total_records}")
        print(f"  Errors: {validation_result.errors}")
        print(f"  Warnings: {validation_result.warnings}")
        
        logger.info("Data cleaning operations completed successfully")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
