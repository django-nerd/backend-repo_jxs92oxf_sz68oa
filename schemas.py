"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Core user schema for potential future auth
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

# Product schema for marketplace listings
class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in INR")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
    image: Optional[str] = Field(None, description="Primary image URL")
    seller_name: Optional[str] = Field(None, description="Seller display name")

# Cart item used inside orders
class OrderItem(BaseModel):
    product_id: str = Field(..., description="Product document ID")
    title: str = Field(..., description="Snapshot of product title")
    price: float = Field(..., ge=0, description="Unit price at checkout")
    quantity: int = Field(..., ge=1, description="Quantity purchased")
    image: Optional[str] = Field(None, description="Snapshot of image URL")

# Order schema for checkout
class Order(BaseModel):
    buyer_name: str = Field(..., description="Buyer name")
    buyer_email: str = Field(..., description="Buyer email")
    items: List[OrderItem] = Field(..., description="Items in this order")
    payment_method: str = Field("COD", description="Payment method e.g. UPI, COD")
    status: str = Field("pending", description="Order status")
    total_amount: float = Field(..., ge=0, description="Computed total amount")
