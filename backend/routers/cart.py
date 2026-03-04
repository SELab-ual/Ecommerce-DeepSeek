from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import uuid

from database import get_db
from models import Cart
from schemas import (
    CartResponse, CartItemCreate, CartItemUpdate,
    CartItemResponse, ProductResponse
)
from auth import get_current_user_optional
import crud

router = APIRouter()

def get_session_id(request: Request) -> str:
    """Get or create session ID for guest users"""
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

@router.get("/", response_model=CartResponse)
async def get_cart(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Get current user's cart (ID 751)"""
    session_id = get_session_id(request)
    
    # Get or create cart
    cart = crud.get_or_create_cart(
        db,
        user_id=current_user.id if current_user else None,
        session_id=session_id if not current_user else None
    )
    
    # Get cart items and calculate totals
    cart_totals = crud.calculate_cart_totals(db, cart.id)
    
    # Prepare response
    cart_items = []
    for item in cart_totals["items"]:
        cart_items.append({
            "id": item.id,
            "product": item.product,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": item.quantity * item.unit_price
        })
    
    response = CartResponse(
        id=cart.id,
        items=cart_items,
        subtotal=cart_totals["subtotal"],
        total_items=cart_totals["total_items"]
    )
    
    return response

@router.post("/items", response_model=CartResponse)
async def add_to_cart(
    request: Request,
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Add item to cart (ID 748)"""
    session_id = get_session_id(request)
    
    # Get or create cart
    cart = crud.get_or_create_cart(
        db,
        user_id=current_user.id if current_user else None,
        session_id=session_id if not current_user else None
    )
    
    # Add item to cart
    try:
        crud.add_to_cart(db, cart.id, item.product_id, item.quantity)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Return updated cart
    return await get_cart(request, db, current_user)

@router.put("/items/{item_id}", response_model=CartResponse)
async def update_cart_item(
    request: Request,
    item_id: str,
    item_update: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Update cart item quantity (ID 759)"""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")
    
    try:
        crud.update_cart_item_quantity(db, item_uuid, item_update.quantity)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return await get_cart(request, db, current_user)

@router.delete("/items/{item_id}", response_model=CartResponse)
async def remove_from_cart(
    request: Request,
    item_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Remove item from cart (ID 760)"""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")
    
    crud.remove_from_cart(db, item_uuid)
    
    return await get_cart(request, db, current_user)

@router.delete("/", response_model=dict)
async def clear_cart(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Clear all items from cart"""
    session_id = get_session_id(request)
    
    cart = crud.get_or_create_cart(
        db,
        user_id=current_user.id if current_user else None,
        session_id=session_id if not current_user else None
    )
    
    crud.clear_cart(db, cart.id)
    
    return {"message": "Cart cleared successfully"}