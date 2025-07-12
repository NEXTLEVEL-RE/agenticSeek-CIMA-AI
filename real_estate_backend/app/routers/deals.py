from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from ..database import get_db
from ..models import Deal, DealStatus, Property, Lead, User
from ..schemas import DealCreate, DealUpdate, Deal as DealSchema
from ..auth import get_current_active_user

router = APIRouter(prefix="/deals", tags=["deals"])

@router.post("/", response_model=DealSchema)
async def create_deal(
    deal: DealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify property and lead exist
    property = db.query(Property).filter(Property.id == deal.property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    lead = db.query(Lead).filter(Lead.id == deal.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Calculate wholesale fee and net profit
    if property.arv and deal.offer_price:
        wholesale_fee = property.arv * 0.10  # 10% wholesale fee
        net_profit = wholesale_fee - (deal.offer_price - property.purchase_price)
    else:
        wholesale_fee = None
        net_profit = None
    
    db_deal = Deal(
        **deal.dict(),
        agent_id=current_user.id,
        wholesale_fee=wholesale_fee,
        net_profit=net_profit
    )
    db.add(db_deal)
    db.commit()
    db.refresh(db_deal)
    return db_deal

@router.get("/", response_model=List[DealSchema])
async def get_deals(
    skip: int = 0,
    limit: int = 100,
    status: Optional[DealStatus] = None,
    agent_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Deal)
    
    if status:
        query = query.filter(Deal.status == status)
    
    if agent_id:
        query = query.filter(Deal.agent_id == agent_id)
    
    deals = query.offset(skip).limit(limit).all()
    return deals

@router.get("/{deal_id}", response_model=DealSchema)
async def get_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal

@router.put("/{deal_id}", response_model=DealSchema)
async def update_deal(
    deal_id: int,
    deal_update: DealUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if db_deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    update_data = deal_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_deal, field, value)
    
    # Recalculate financials if offer price changed
    if 'offer_price' in update_data and db_deal.property.arv:
        db_deal.wholesale_fee = db_deal.property.arv * 0.10
        db_deal.net_profit = db_deal.wholesale_fee - (db_deal.offer_price - db_deal.property.purchase_price)
    
    db.commit()
    db.refresh(db_deal)
    return db_deal

@router.delete("/{deal_id}")
async def delete_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if db_deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    db.delete(db_deal)
    db.commit()
    return {"message": "Deal deleted successfully"}

@router.put("/{deal_id}/status")
async def update_deal_status(
    deal_id: int,
    status: DealStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if db_deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    db_deal.status = status
    
    # Update property status if deal is closed
    if status == DealStatus.CLOSED:
        db_deal.property.status = "sold"
        db_deal.property.sold_date = datetime.utcnow()
    
    db.commit()
    db.refresh(db_deal)
    return {"message": f"Deal status updated to {status}"}

@router.get("/analytics/summary")
async def get_deals_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Total deals
    total_deals = db.query(func.count(Deal.id)).scalar()
    
    # Deals by status
    deals_by_status = db.query(
        Deal.status,
        func.count(Deal.id)
    ).group_by(Deal.status).all()
    
    # Total revenue
    total_revenue = db.query(func.sum(Deal.net_profit)).filter(
        Deal.status == DealStatus.CLOSED
    ).scalar() or 0
    
    # Monthly revenue (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    monthly_revenue = db.query(func.sum(Deal.net_profit)).filter(
        Deal.status == DealStatus.CLOSED,
        Deal.created_at >= thirty_days_ago
    ).scalar() or 0
    
    return {
        "total_deals": total_deals,
        "deals_by_status": dict(deals_by_status),
        "total_revenue": float(total_revenue),
        "monthly_revenue": float(monthly_revenue)
    } 