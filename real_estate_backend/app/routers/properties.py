from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..database import get_db
from ..models import Property, PropertyStatus, User
from ..schemas import PropertyCreate, PropertyUpdate, Property as PropertySchema, PropertySearch
from ..auth import get_current_active_user

router = APIRouter(prefix="/properties", tags=["properties"])

@router.post("/", response_model=PropertySchema)
async def create_property(
    property: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_property = Property(**property.dict())
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property

@router.get("/", response_model=List[PropertySchema])
async def get_properties(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[PropertyStatus] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Property)
    
    if search:
        query = query.filter(
            or_(
                Property.address.contains(search),
                Property.city.contains(search),
                Property.state.contains(search)
            )
        )
    
    if status:
        query = query.filter(Property.status == status)
    
    if city:
        query = query.filter(Property.city == city)
    
    if state:
        query = query.filter(Property.state == state)
    
    properties = query.offset(skip).limit(limit).all()
    return properties

@router.get("/{property_id}", response_model=PropertySchema)
async def get_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    property = db.query(Property).filter(Property.id == property_id).first()
    if property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return property

@router.put("/{property_id}", response_model=PropertySchema)
async def update_property(
    property_id: int,
    property_update: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_property = db.query(Property).filter(Property.id == property_id).first()
    if db_property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    
    update_data = property_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_property, field, value)
    
    db.commit()
    db.refresh(db_property)
    return db_property

@router.delete("/{property_id}")
async def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_property = db.query(Property).filter(Property.id == property_id).first()
    if db_property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    
    db.delete(db_property)
    db.commit()
    return {"message": "Property deleted successfully"}

@router.get("/search/", response_model=List[PropertySchema])
async def search_properties(
    search_params: PropertySearch = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Property)
    
    if search_params.address:
        query = query.filter(Property.address.contains(search_params.address))
    
    if search_params.city:
        query = query.filter(Property.city == search_params.city)
    
    if search_params.state:
        query = query.filter(Property.state == search_params.state)
    
    if search_params.property_type:
        query = query.filter(Property.property_type == search_params.property_type)
    
    if search_params.status:
        query = query.filter(Property.status == search_params.status)
    
    if search_params.min_price:
        query = query.filter(Property.purchase_price >= search_params.min_price)
    
    if search_params.max_price:
        query = query.filter(Property.purchase_price <= search_params.max_price)
    
    properties = query.all()
    return properties 