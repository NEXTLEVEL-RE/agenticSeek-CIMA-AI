from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from ..database import get_db
from ..models import Property, Lead, Deal, PropertyStatus, LeadStatus, DealStatus, User
from ..schemas import DashboardStats
from ..auth import get_current_active_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Property stats
    total_properties = db.query(func.count(Property.id)).scalar()
    available_properties = db.query(func.count(Property.id)).filter(
        Property.status == PropertyStatus.AVAILABLE
    ).scalar()
    
    # Lead stats
    total_leads = db.query(func.count(Lead.id)).scalar()
    new_leads = db.query(func.count(Lead.id)).filter(
        Lead.status == LeadStatus.NEW
    ).scalar()
    
    # Deal stats
    total_deals = db.query(func.count(Deal.id)).scalar()
    pending_deals = db.query(func.count(Deal.id)).filter(
        Deal.status == DealStatus.PENDING
    ).scalar()
    
    # Revenue stats
    total_revenue = db.query(func.sum(Deal.net_profit)).filter(
        Deal.status == DealStatus.CLOSED
    ).scalar() or 0
    
    # Monthly revenue (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    monthly_revenue = db.query(func.sum(Deal.net_profit)).filter(
        Deal.status == DealStatus.CLOSED,
        Deal.created_at >= thirty_days_ago
    ).scalar() or 0
    
    return DashboardStats(
        total_properties=total_properties,
        available_properties=available_properties,
        total_leads=total_leads,
        new_leads=new_leads,
        total_deals=total_deals,
        pending_deals=pending_deals,
        total_revenue=float(total_revenue),
        monthly_revenue=float(monthly_revenue)
    )

@router.get("/recent-activity")
async def get_recent_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Recent properties
    recent_properties = db.query(Property).order_by(
        Property.created_at.desc()
    ).limit(5).all()
    
    # Recent leads
    recent_leads = db.query(Lead).order_by(
        Lead.created_at.desc()
    ).limit(5).all()
    
    # Recent deals
    recent_deals = db.query(Deal).order_by(
        Deal.created_at.desc()
    ).limit(5).all()
    
    return {
        "recent_properties": recent_properties,
        "recent_leads": recent_leads,
        "recent_deals": recent_deals
    }

@router.get("/property-status-distribution")
async def get_property_status_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    status_counts = db.query(
        Property.status,
        func.count(Property.id)
    ).group_by(Property.status).all()
    
    return dict(status_counts)

@router.get("/lead-status-distribution")
async def get_lead_status_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    status_counts = db.query(
        Lead.status,
        func.count(Lead.id)
    ).group_by(Lead.status).all()
    
    return dict(status_counts)

@router.get("/deal-status-distribution")
async def get_deal_status_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    status_counts = db.query(
        Deal.status,
        func.count(Deal.id)
    ).group_by(Deal.status).all()
    
    return dict(status_counts)

@router.get("/monthly-revenue")
async def get_monthly_revenue(
    months: int = 6,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Get revenue for the last N months
    monthly_data = []
    for i in range(months):
        start_date = datetime.utcnow() - timedelta(days=30 * (i + 1))
        end_date = datetime.utcnow() - timedelta(days=30 * i)
        
        revenue = db.query(func.sum(Deal.net_profit)).filter(
            Deal.status == DealStatus.CLOSED,
            Deal.created_at >= start_date,
            Deal.created_at < end_date
        ).scalar() or 0
        
        monthly_data.append({
            "month": start_date.strftime("%Y-%m"),
            "revenue": float(revenue)
        })
    
    return monthly_data[::-1]  # Reverse to show oldest first 