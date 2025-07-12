from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..database import get_db
from ..models import Lead, LeadStatus, User
from ..schemas import LeadCreate, LeadUpdate, Lead as LeadSchema, LeadSearch
from ..auth import get_current_active_user

router = APIRouter(prefix="/leads", tags=["leads"])

@router.post("/", response_model=LeadSchema)
async def create_lead(
    lead: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_lead = Lead(**lead.dict())
    if not db_lead.assigned_to_id:
        db_lead.assigned_to_id = current_user.id
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

@router.get("/", response_model=List[LeadSchema])
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    status: Optional[LeadStatus] = None,
    assigned_to_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Lead)
    
    if status:
        query = query.filter(Lead.status == status)
    
    if assigned_to_id:
        query = query.filter(Lead.assigned_to_id == assigned_to_id)
    
    if search:
        query = query.filter(
            or_(
                Lead.first_name.contains(search),
                Lead.last_name.contains(search),
                Lead.email.contains(search),
                Lead.address.contains(search),
                Lead.city.contains(search)
            )
        )
    
    leads = query.offset(skip).limit(limit).all()
    return leads

@router.get("/{lead_id}", response_model=LeadSchema)
async def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.put("/{lead_id}", response_model=LeadSchema)
async def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    update_data = lead_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_lead, field, value)
    
    db.commit()
    db.refresh(db_lead)
    return db_lead

@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(db_lead)
    db.commit()
    return {"message": "Lead deleted successfully"}

@router.get("/search/", response_model=List[LeadSchema])
async def search_leads(
    search_params: LeadSearch = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Lead)
    
    if search_params.name:
        query = query.filter(
            or_(
                Lead.first_name.contains(search_params.name),
                Lead.last_name.contains(search_params.name)
            )
        )
    
    if search_params.city:
        query = query.filter(Lead.city == search_params.city)
    
    if search_params.status:
        query = query.filter(Lead.status == search_params.status)
    
    if search_params.assigned_to_id:
        query = query.filter(Lead.assigned_to_id == search_params.assigned_to_id)
    
    leads = query.all()
    return leads

@router.put("/{lead_id}/status")
async def update_lead_status(
    lead_id: int,
    status: LeadStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db_lead.status = status
    db.commit()
    db.refresh(db_lead)
    return {"message": f"Lead status updated to {status}"} 