from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from database import get_db
from models import Order, User
from schemas import OrderCreate, OrderResponse
from auth import get_current_user_optional, get_current_active_user
import crud

router = APIRouter()

def get_session_id(request: Request) -> str:
    """Get or create session ID for guest users"""
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: Request,
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Create a new order from cart (ID 572, 582, 888, 932, 933)"""
    session_id = get_session_id(request)
    
    try:
        order = crud.create_order(
            db,
            user_id=current_user.id if current_user else None,
            session_id=session_id if not current_user else None,
            order_data=order_data
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return order

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Get order details (ID 582)"""
    try:
        order_uuid = uuid.UUID(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order ID format")
    
    order = crud.get_order(db, order_uuid)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check authorization
    if order.user_id and (not current_user or current_user.id != order.user_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return order

@router.get("/number/{order_number}", response_model=OrderResponse)
async def get_order_by_number(
    order_number: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Get order by order number"""
    order = crud.get_order_by_number(db, order_number)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check authorization
    if order.user_id and (not current_user or current_user.id != order.user_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return order

@router.get("/", response_model=List[OrderResponse])
async def get_my_orders(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Get user's order history"""
    session_id = get_session_id(request)
    
    if current_user:
        orders = crud.get_user_orders(db, current_user.id, skip, limit)
    else:
        orders = crud.get_guest_orders(db, session_id, skip, limit)
    
    return orders

@router.post("/{order_id}/confirm")
async def confirm_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Confirm order completion (ID 888, 934)"""
    try:
        order_uuid = uuid.UUID(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order ID format")
    
    order = crud.get_order(db, order_uuid)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update order status
    order.status = "completed"
    db.commit()
    
    return {
        "message": "Order confirmed successfully",
        "order_number": order.order_number,
        "status": order.status
    }