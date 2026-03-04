from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from database import get_db
from models import Product
from schemas import ProductResponse, ProductCreate
from auth import get_current_active_user
import crud

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    product_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of products with optional filtering (ID 586)"""
    products = crud.get_products(db, skip=skip, limit=limit, product_type=product_type, search=search)
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get a single product by ID"""
    try:
        product_uuid = uuid.UUID(product_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid product ID format")
    
    product = crud.get_product(db, product_uuid)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

@router.get("/isbn/{isbn}", response_model=ProductResponse)
async def get_product_by_isbn(
    isbn: str,
    db: Session = Depends(get_db)
):
    """Get a product by ISBN"""
    product = crud.get_product_by_isbn(db, isbn)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

# Admin endpoints (protected)
@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new product (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return crud.create_product(db, product)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_update: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update a product (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        product_uuid = uuid.UUID(product_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid product ID format")
    
    product = crud.get_product(db, product_uuid)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in product_update.items():
        if hasattr(product, key) and value is not None:
            setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return product