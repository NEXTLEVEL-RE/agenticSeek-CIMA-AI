from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from .models import UserRole, PropertyStatus, LeadStatus, DealStatus

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    role: UserRole = UserRole.AGENT
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Property schemas
class PropertyBase(BaseModel):
    address: str
    city: str
    state: str
    zip_code: str
    property_type: str
    square_feet: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    year_built: Optional[int] = None
    arv: Optional[float] = None
    purchase_price: Optional[float] = None
    repair_cost: Optional[float] = None
    holding_cost: Optional[float] = None
    selling_price: Optional[float] = None
    description: Optional[str] = None
    notes: Optional[str] = None

class PropertyCreate(PropertyBase):
    owner_id: int

class PropertyUpdate(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    property_type: Optional[str] = None
    square_feet: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    year_built: Optional[int] = None
    arv: Optional[float] = None
    purchase_price: Optional[float] = None
    repair_cost: Optional[float] = None
    holding_cost: Optional[float] = None
    selling_price: Optional[float] = None
    status: Optional[PropertyStatus] = None
    description: Optional[str] = None
    notes: Optional[str] = None

class Property(PropertyBase):
    id: int
    status: PropertyStatus
    owner_id: int
    list_date: datetime
    sold_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Lead schemas
class LeadBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    property_type: Optional[str] = None
    estimated_value: Optional[float] = None
    reason_for_selling: Optional[str] = None
    timeline: Optional[str] = None
    notes: Optional[str] = None

class LeadCreate(LeadBase):
    assigned_to_id: Optional[int] = None

class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    property_type: Optional[str] = None
    estimated_value: Optional[float] = None
    reason_for_selling: Optional[str] = None
    timeline: Optional[str] = None
    status: Optional[LeadStatus] = None
    assigned_to_id: Optional[int] = None
    notes: Optional[str] = None
    next_follow_up: Optional[datetime] = None

class Lead(LeadBase):
    id: int
    status: LeadStatus
    assigned_to_id: Optional[int] = None
    next_follow_up: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Deal schemas
class DealBase(BaseModel):
    property_id: int
    lead_id: int
    offer_price: float
    closing_date: Optional[datetime] = None
    wholesale_fee: Optional[float] = None
    net_profit: Optional[float] = None
    notes: Optional[str] = None

class DealCreate(DealBase):
    agent_id: int

class DealUpdate(BaseModel):
    offer_price: Optional[float] = None
    status: Optional[DealStatus] = None
    closing_date: Optional[datetime] = None
    wholesale_fee: Optional[float] = None
    net_profit: Optional[float] = None
    notes: Optional[str] = None

class Deal(DealBase):
    id: int
    agent_id: int
    status: DealStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Dashboard schemas
class DashboardStats(BaseModel):
    total_properties: int
    available_properties: int
    total_leads: int
    new_leads: int
    total_deals: int
    pending_deals: int
    total_revenue: float
    monthly_revenue: float

# Search and filter schemas
class PropertySearch(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    property_type: Optional[str] = None
    status: Optional[PropertyStatus] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

class LeadSearch(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    status: Optional[LeadStatus] = None
    assigned_to_id: Optional[int] = None 