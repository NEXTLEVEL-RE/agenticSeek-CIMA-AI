from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    AGENT = "agent"
    INVESTOR = "investor"

class PropertyStatus(str, enum.Enum):
    AVAILABLE = "available"
    UNDER_CONTRACT = "under_contract"
    SOLD = "sold"
    OFF_MARKET = "off_market"

class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    CONVERTED = "converted"

class DealStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CLOSED = "closed"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.AGENT)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    properties = relationship("Property", back_populates="owner")
    leads = relationship("Lead", back_populates="assigned_to")
    deals = relationship("Deal", back_populates="agent")

class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    property_type = Column(String)  # Single family, multi-family, commercial, etc.
    square_feet = Column(Float)
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    year_built = Column(Integer)
    
    # Financial
    arv = Column(Float)  # After Repair Value
    purchase_price = Column(Float)
    repair_cost = Column(Float)
    holding_cost = Column(Float)
    selling_price = Column(Float)
    
    # Status and dates
    status = Column(Enum(PropertyStatus), default=PropertyStatus.AVAILABLE)
    list_date = Column(DateTime(timezone=True), server_default=func.now())
    sold_date = Column(DateTime(timezone=True))
    
    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="properties")
    
    # Additional info
    description = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    
    # Lead details
    property_type = Column(String)
    estimated_value = Column(Float)
    reason_for_selling = Column(String)
    timeline = Column(String)
    
    # Status
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    assigned_to = relationship("User", back_populates="leads")
    
    # Notes and follow-up
    notes = Column(Text)
    next_follow_up = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Deal(Base):
    __tablename__ = "deals"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    lead_id = Column(Integer, ForeignKey("leads.id"))
    agent_id = Column(Integer, ForeignKey("users.id"))
    
    # Deal details
    status = Column(Enum(DealStatus), default=DealStatus.PENDING)
    offer_price = Column(Float)
    closing_date = Column(DateTime(timezone=True))
    
    # Financial calculations
    wholesale_fee = Column(Float)
    net_profit = Column(Float)
    
    # Notes
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    agent = relationship("User", back_populates="deals")
    property = relationship("Property")
    lead = relationship("Lead") 