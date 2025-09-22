"""
Order service for database operations and data cleaning.
"""
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from loguru import logger

from src.database.connection import db_connection
from src.models.order import Order, OrderCleaningResult


class OrderService:
    """Service class for order-related operations."""
    
    def __init__(self):
        self.db = db_connection
    
    def get_all_orders(self) -> List[Dict[str, Any]]:
        """Retrieve all orders from the database."""
        try:
            query = "SELECT * FROM orders ORDER BY order_id"
            orders = self.db.execute_query(query)
            logger.info(f"Retrieved {len(orders)} orders from database")
            return orders
        except Exception as e:
            logger.error(f"Failed to retrieve orders: {e}")
            raise
    
    def get_orders_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Retrieve orders by status."""
        try:
            query = "SELECT * FROM orders WHERE status = %(status)s ORDER BY order_id"
            orders = self.db.execute_query(query, {"status": status})
            logger.info(f"Retrieved {len(orders)} orders with status '{status}'")
            return orders
        except Exception as e:
            logger.error(f"Failed to retrieve orders by status: {e}")
            raise
    
    def get_orders_dataframe(self) -> pd.DataFrame:
        """Get all orders as a pandas DataFrame for data analysis."""
        try:
            orders = self.get_all_orders()
            df = pd.DataFrame(orders)
            logger.info(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.error(f"Failed to create DataFrame: {e}")
            raise
    
    def clean_duplicate_orders(self) -> OrderCleaningResult:
        """Remove duplicate orders based on business logic."""
        try:
            # Get all orders
            orders_df = self.get_orders_dataframe()
            total_records = len(orders_df)
            
            # Identify duplicates based on business logic
            # Duplicates: same customer, same date, same category, same quantity
            duplicates = orders_df.duplicated(
                subset=['customer_name', 'order_date', 'category', 'quantity', 'subtotal_amount'], 
                keep='first'
            )
            duplicate_count = duplicates.sum()
            
            if duplicate_count > 0:
                # Get duplicate records for review
                duplicate_records = orders_df[duplicates]
                logger.warning(f"Found {duplicate_count} duplicate orders")
                
                # Log some examples of duplicates
                for idx, row in duplicate_records.head(5).iterrows():
                    logger.warning(f"Duplicate: Customer={row['customer_name']}, Date={row['order_date']}, Category={row['category']}")
                
                return OrderCleaningResult(
                    total_records=total_records,
                    cleaned_records=duplicate_count,
                    errors=0,
                    warnings=duplicate_count,
                    cleaning_summary={
                        "duplicates_found": duplicate_count,
                        "duplicate_examples": duplicate_records[['order_id', 'customer_name', 'order_date', 'category']].head(10).to_dict('records')
                    }
                )
            else:
                logger.info("No duplicate orders found")
                return OrderCleaningResult(
                    total_records=total_records,
                    cleaned_records=0,
                    errors=0,
                    warnings=0,
                    cleaning_summary={"duplicates_found": 0}
                )
                
        except Exception as e:
            logger.error(f"Failed to clean duplicate orders: {e}")
            raise
    
    def clean_incomplete_records(self) -> OrderCleaningResult:
        """Clean incomplete records - missing required fields or invalid data."""
        try:
            orders_df = self.get_orders_dataframe()
            total_records = len(orders_df)
            errors = 0
            warnings = 0
            incomplete_records = []
            
            # Check for null values in required fields
            required_fields = ['status', 'customer_name', 'order_date', 'quantity', 
                             'subtotal_amount', 'tax_rate', 'shipping_cost', 'category', 'subcategory']
            
            null_counts = orders_df[required_fields].isnull().sum()
            total_nulls = null_counts.sum()
            
            if total_nulls > 0:
                logger.warning(f"Found {total_nulls} null values in required fields")
                warnings += total_nulls
                
                # Get records with null values
                for field in required_fields:
                    if null_counts[field] > 0:
                        null_records = orders_df[orders_df[field].isnull()]
                        incomplete_records.extend(null_records['order_id'].tolist())
                        logger.warning(f"Field '{field}' has {null_counts[field]} null values")
            
            # Check for empty strings in text fields
            text_fields = ['status', 'customer_name', 'category', 'subcategory']
            for field in text_fields:
                empty_strings = (orders_df[field] == '').sum()
                if empty_strings > 0:
                    logger.warning(f"Field '{field}' has {empty_strings} empty strings")
                    warnings += empty_strings
                    empty_records = orders_df[orders_df[field] == '']
                    incomplete_records.extend(empty_records['order_id'].tolist())
            
            # Check for negative values in numeric fields
            numeric_fields = ['quantity', 'subtotal_amount', 'tax_rate', 'shipping_cost']
            for field in numeric_fields:
                negative_values = (orders_df[field] < 0).sum()
                if negative_values > 0:
                    logger.error(f"Field '{field}' has {negative_values} negative values")
                    errors += negative_values
                    negative_records = orders_df[orders_df[field] < 0]
                    incomplete_records.extend(negative_records['order_id'].tolist())
            
            # Check for invalid tax rates (> 100%)
            invalid_tax_rates = (orders_df['tax_rate'] > 1.0).sum()
            if invalid_tax_rates > 0:
                logger.error(f"Found {invalid_tax_rates} invalid tax rates (> 100%)")
                errors += invalid_tax_rates
                invalid_tax_records = orders_df[orders_df['tax_rate'] > 1.0]
                incomplete_records.extend(invalid_tax_records['order_id'].tolist())
            
            # Remove duplicates from incomplete records list
            incomplete_records = list(set(incomplete_records))
            
            return OrderCleaningResult(
                total_records=total_records,
                cleaned_records=len(incomplete_records),
                errors=errors,
                warnings=warnings,
                cleaning_summary={
                    "incomplete_records": len(incomplete_records),
                    "null_values": null_counts.to_dict(),
                    "errors_found": errors,
                    "warnings_found": warnings,
                    "problematic_order_ids": incomplete_records[:20]  # Show first 20
                }
            )
                
        except Exception as e:
            logger.error(f"Failed to clean incomplete records: {e}")
            raise
    
    def validate_data_types(self) -> OrderCleaningResult:
        """Validate data types and business rules in orders data."""
        try:
            orders_df = self.get_orders_dataframe()
            total_records = len(orders_df)
            errors = 0
            warnings = 0
            validation_issues = []
            
            # Validate numeric fields
            numeric_fields = {
                'quantity': 'integer',
                'subtotal_amount': 'decimal',
                'tax_rate': 'decimal',
                'shipping_cost': 'decimal'
            }
            
            for field, expected_type in numeric_fields.items():
                if field in orders_df.columns:
                    # Check for non-numeric values
                    invalid_numeric = pd.to_numeric(orders_df[field], errors='coerce').isnull().sum()
                    if invalid_numeric > 0:
                        warnings += invalid_numeric
                        logger.warning(f"Found {invalid_numeric} invalid {field} values (non-numeric)")
                        validation_issues.append(f"{field}: {invalid_numeric} non-numeric values")
            
            # Validate date field
            if 'order_date' in orders_df.columns:
                invalid_dates = pd.to_datetime(orders_df['order_date'], errors='coerce').isnull().sum()
                if invalid_dates > 0:
                    warnings += invalid_dates
                    logger.warning(f"Found {invalid_dates} invalid order_date values")
                    validation_issues.append(f"order_date: {invalid_dates} invalid dates")
            
            # Validate business rules
            # Check for reasonable quantity values
            if 'quantity' in orders_df.columns:
                extreme_quantities = ((orders_df['quantity'] > 1000) | (orders_df['quantity'] == 0)).sum()
                if extreme_quantities > 0:
                    warnings += extreme_quantities
                    logger.warning(f"Found {extreme_quantities} extreme quantity values (0 or >1000)")
                    validation_issues.append(f"quantity: {extreme_quantities} extreme values")
            
            # Check for reasonable amounts
            if 'subtotal_amount' in orders_df.columns:
                extreme_amounts = (orders_df['subtotal_amount'] > 100000).sum()
                if extreme_amounts > 0:
                    warnings += extreme_amounts
                    logger.warning(f"Found {extreme_amounts} extreme subtotal_amount values (>100,000)")
                    validation_issues.append(f"subtotal_amount: {extreme_amounts} extreme values")
            
            # Check for reasonable shipping costs
            if 'shipping_cost' in orders_df.columns:
                extreme_shipping = (orders_df['shipping_cost'] > 1000).sum()
                if extreme_shipping > 0:
                    warnings += extreme_shipping
                    logger.warning(f"Found {extreme_shipping} extreme shipping_cost values (>1000)")
                    validation_issues.append(f"shipping_cost: {extreme_shipping} extreme values")
            
            # Validate status values
            if 'status' in orders_df.columns:
                valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled', 'returned']
                invalid_statuses = (~orders_df['status'].str.lower().isin(valid_statuses)).sum()
                if invalid_statuses > 0:
                    warnings += invalid_statuses
                    logger.warning(f"Found {invalid_statuses} invalid status values")
                    validation_issues.append(f"status: {invalid_statuses} invalid values")
            
            return OrderCleaningResult(
                total_records=total_records,
                cleaned_records=0,
                errors=errors,
                warnings=warnings,
                cleaning_summary={
                    "validation_issues": validation_issues,
                    "data_type_errors": errors,
                    "data_type_warnings": warnings
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to validate data types: {e}")
            raise
    
    def _convert_pandas_to_dict(self, pandas_obj):
        """Convert pandas objects to native Python types for JSON serialization."""
        import numpy as np
        
        if hasattr(pandas_obj, 'to_dict'):
            # For DataFrames and Series
            result = pandas_obj.to_dict()
            # Convert numpy types to native Python types
            if isinstance(result, dict):
                for key, value in result.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, (np.integer, np.int64, np.int32)):
                                result[key][sub_key] = int(sub_value)
                            elif isinstance(sub_value, (np.floating, np.float64, np.float32)):
                                result[key][sub_key] = float(sub_value)
                            elif isinstance(sub_value, np.ndarray):
                                result[key][sub_key] = sub_value.tolist()
                    else:
                        if isinstance(value, (np.integer, np.int64, np.int32)):
                            result[key] = int(value)
                        elif isinstance(value, (np.floating, np.float64, np.float32)):
                            result[key] = float(value)
                        elif isinstance(value, np.ndarray):
                            result[key] = value.tolist()
            return result
        else:
            return str(pandas_obj)

    def get_data_quality_report(self) -> Dict[str, Any]:
        """Generate a comprehensive data quality report."""
        try:
            orders_df = self.get_orders_dataframe()
            
            # Calculate basic metrics
            total_records = len(orders_df)
            total_columns = len(orders_df.columns)
            duplicate_records = int(orders_df.duplicated().sum())
            
            # Calculate null values for each column
            null_values = {}
            for column in orders_df.columns:
                null_count = int(orders_df[column].isnull().sum())
                null_values[column] = null_count
            
            # Calculate data completeness percentage
            completeness = {}
            for column in orders_df.columns:
                non_null_count = orders_df[column].notna().sum()
                completeness[column] = round((non_null_count / total_records) * 100, 2)
            
            # Calculate value distributions for key fields (simplified)
            distributions = {}
            if 'status' in orders_df.columns:
                status_counts = orders_df['status'].value_counts()
                distributions['status'] = {str(k): int(v) for k, v in status_counts.items()}
            
            if 'category' in orders_df.columns:
                category_counts = orders_df['category'].value_counts().head(10)
                distributions['category'] = {str(k): int(v) for k, v in category_counts.items()}
            
            # Basic statistics (simplified)
            basic_stats = {}
            numeric_columns = orders_df.select_dtypes(include=['number']).columns
            if len(numeric_columns) > 0:
                for col in numeric_columns:
                    basic_stats[col] = {
                        'count': int(orders_df[col].count()),
                        'mean': float(orders_df[col].mean()) if not orders_df[col].isna().all() else 0.0,
                        'min': float(orders_df[col].min()) if not orders_df[col].isna().all() else 0.0,
                        'max': float(orders_df[col].max()) if not orders_df[col].isna().all() else 0.0
                    }
            
            report = {
                "total_records": total_records,
                "total_columns": total_columns,
                "null_values": null_values,
                "duplicate_records": duplicate_records,
                "data_completeness": completeness,
                "value_distributions": distributions,
                "basic_statistics": basic_stats
            }
            
            logger.info("Data quality report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate data quality report: {e}")
            raise
    
    def update_order(self, order_id: int, update_data: Dict[str, Any]) -> bool:
        """Update a specific order."""
        try:
            # Build dynamic update query
            set_clauses = []
            params = {"order_id": order_id}
            
            for key, value in update_data.items():
                set_clauses.append(f"{key} = %({key})s")
                params[key] = value
            
            query = f"UPDATE orders SET {', '.join(set_clauses)} WHERE order_id = %(order_id)s"
            
            affected_rows = self.db.execute_update(query, params)
            
            if affected_rows > 0:
                logger.info(f"Successfully updated order {order_id}")
                return True
            else:
                logger.warning(f"No order found with id {order_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update order {order_id}: {e}")
            raise
