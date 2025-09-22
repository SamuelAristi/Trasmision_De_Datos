"""
Order model for the orders table.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import date
from decimal import Decimal


class OrderBase(BaseModel):
    """Base order model with common fields."""
    
    order_id: Optional[int] = Field(None, description="Primary key - bigint")
    status: str = Field(..., description="Order status - text NOT NULL")
    customer_name: str = Field(..., description="Customer name - text NOT NULL")
    order_date: date = Field(..., description="Order date - date NOT NULL")
    quantity: int = Field(..., ge=0, description="Quantity - integer NOT NULL CHECK (quantity >= 0)")
    subtotal_amount: Decimal = Field(..., ge=0, description="Subtotal amount - numeric(18,2) NOT NULL CHECK (subtotal_amount >= 0)")
    tax_rate: Decimal = Field(..., ge=0, description="Tax rate - numeric(6,4) NOT NULL CHECK (tax_rate >= 0)")
    shipping_cost: Decimal = Field(..., ge=0, description="Shipping cost - numeric(18,2) NOT NULL CHECK (shipping_cost >= 0)")
    category: str = Field(..., description="Product category - text NOT NULL")
    subcategory: str = Field(..., description="Product subcategory - text NOT NULL")
    
    @field_validator('tax_rate')
    @classmethod
    def validate_tax_rate(cls, v):
        """Validate tax rate is within reasonable bounds (0-100%)."""
        if v > 1.0:  # 100%
            raise ValueError('Tax rate cannot exceed 100% (1.0)')
        return v
    
    class Config:
        from_attributes = True


class OrderCreate(OrderBase):
    """Model for creating new orders."""
    pass


class OrderUpdate(OrderBase):
    """Model for updating existing orders."""
    pass


class Order(OrderBase):
    """Complete order model."""
    order_id: int = Field(..., description="Primary key - bigint")
    
    class Config:
        from_attributes = True


class OrderCleaningResult(BaseModel):
    """Model for data cleaning results."""
    total_records: int
    cleaned_records: int
    errors: int
    warnings: int
    cleaning_summary: Dict[str, Any]
    
    class Config:
        from_attributes = True
