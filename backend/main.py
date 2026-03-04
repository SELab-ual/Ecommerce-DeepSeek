from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
import logging
from typing import Optional

from database import engine, get_db
from models import Base
from routers import products, cart, users, orders
from auth import get_current_user
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Sprint 1 E-commerce API",
    description="Foundation API for the e-commerce platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:80", "http://frontend"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(cart.router, prefix="/api/cart", tags=["cart"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Sprint 1 E-commerce API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    try:
        # Test database connection
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "environment": settings.ENVIRONMENT
    }

@app.get("/api/search")
async def search_products(
    q: Optional[str] = None,
    sort: str = "relevance",
    page: int = 1,
    limit: int = 20,
    db = Depends(get_db)
):
    """Basic search functionality (ID 586)"""
    from sqlalchemy import or_
    from models import Product
    
    query = db.query(Product).filter(Product.is_active == True)
    
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Product.title.ilike(search_term),
                Product.author.ilike(search_term),
                Product.isbn13.ilike(search_term),
                Product.publisher.ilike(search_term)
            )
        )
    
    # Sorting (ID 916)
    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort == "title":
        query = query.order_by(Product.title)
    else:  # relevance or default
        query = query.order_by(Product.title)
    
    total = query.count()
    products = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "results": products,
        "query": q
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)