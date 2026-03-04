from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid
from datetime import datetime, timedelta
import random
import string

from models import User, Product, Cart, CartItem, Order, OrderItem, Session as DbSession
from schemas import UserCreate, ProductCreate, OrderCreate
from auth import get_password_hash

# User CRUD
def get_user(db: Session, user_id: uuid.UUID) -> User:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_last_login(db: Session, user_id: uuid.UUID) -> User:
    user = get_user(db, user_id)
    if user:
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user

# Product CRUD
def get_product(db: Session, product_id: uuid.UUID) -> Product:
    return db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()

def get_product_by_isbn(db: Session, isbn: str) -> Product:
    return db.query(Product).filter(Product.isbn13 == isbn, Product.is_active == True).first()

def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    product_type: str = None,
    search: str = None
):
    query = db.query(Product).filter(Product.is_active == True)
    
    if product_type:
        query = query.filter(Product.product_type == product_type)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Product.title.ilike(search_term)) |
            (Product.author.ilike(search_term)) |
            (Product.isbn13.ilike(search_term))
        )
    
    return query.offset(skip).limit(limit).all()

def create_product(db: Session, product: ProductCreate) -> Product:
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Cart CRUD
def get_or_create_cart(db: Session, user_id: uuid.UUID = None, session_id: str = None) -> Cart:
    if user_id:
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    else:
        cart = db.query(Cart).filter(Cart.session_id == session_id).first()
    
    if not cart:
        cart = Cart(
            user_id=user_id,
            session_id=session_id
        )
        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    return cart

def get_cart_items(db: Session, cart_id: uuid.UUID):
    return db.query(CartItem).filter(CartItem.cart_id == cart_id).all()

def add_to_cart(
    db: Session,
    cart_id: uuid.UUID,
    product_id: uuid.UUID,
    quantity: int = 1
) -> CartItem:
    # Check if item already in cart
    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart_id,
        CartItem.product_id == product_id
    ).first()
    
    product = get_product(db, product_id)
    if not product:
        raise ValueError("Product not found")
    
    if cart_item:
        # Update quantity
        cart_item.quantity += quantity
        cart_item.unit_price = product.price
        cart_item.updated_at = datetime.utcnow()
    else:
        # Create new cart item
        cart_item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=product.price
        )
        db.add(cart_item)
    
    db.commit()
    db.refresh(cart_item)
    return cart_item

def update_cart_item_quantity(
    db: Session,
    cart_item_id: uuid.UUID,
    quantity: int
) -> CartItem:
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not cart_item:
        raise ValueError("Cart item not found")
    
    cart_item.quantity = quantity
    cart_item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(cart_item)
    return cart_item

def remove_from_cart(db: Session, cart_item_id: uuid.UUID):
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if cart_item:
        db.delete(cart_item)
        db.commit()
    return cart_item

def clear_cart(db: Session, cart_id: uuid.UUID):
    db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
    db.commit()

def calculate_cart_totals(db: Session, cart_id: uuid.UUID) -> dict:
    items = get_cart_items(db, cart_id)
    subtotal = sum(item.quantity * item.unit_price for item in items)
    total_items = sum(item.quantity for item in items)
    
    return {
        "subtotal": subtotal,
        "total_items": total_items,
        "items": items
    }

# Order CRUD
def generate_order_number() -> str:
    """Generate a unique order number"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ORD-{timestamp}-{random_part}"

def create_order(
    db: Session,
    user_id: uuid.UUID,
    session_id: str,
    order_data: OrderCreate
) -> Order:
    # Get cart
    cart = get_or_create_cart(db, user_id, session_id)
    cart_totals = calculate_cart_totals(db, cart.id)
    
    if cart_totals["total_items"] == 0:
        raise ValueError("Cart is empty")
    
    # Calculate totals
    subtotal = cart_totals["subtotal"]
    shipping_cost = order_data.shipping_cost
    tax_amount = subtotal * 0.19  # 19% VAT (German standard)
    total_amount = subtotal + shipping_cost + tax_amount
    
    # Create order
    order_number = generate_order_number()
    db_order = Order(
        order_number=order_number,
        user_id=user_id,
        session_id=session_id if not user_id else None,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        tax_amount=tax_amount,
        total_amount=total_amount,
        shipping_address=order_data.shipping_address.model_dump(),
        billing_address=order_data.billing_address.model_dump() if order_data.billing_address else order_data.shipping_address.model_dump(),
        payment_method=order_data.payment_method,
        status="pending",
        payment_status="pending"
    )
    
    db.add(db_order)
    db.flush()
    
    # Create order items
    for cart_item in cart_totals["items"]:
        order_item = OrderItem(
            order_id=db_order.id,
            product_id=cart_item.product_id,
            product_title=cart_item.product.title,
            quantity=cart_item.quantity,
            unit_price=cart_item.unit_price,
            total_price=cart_item.quantity * cart_item.unit_price
        )
        db.add(order_item)
    
    # Clear cart
    clear_cart(db, cart.id)
    
    db.commit()
    db.refresh(db_order)
    
    return db_order

def get_order(db: Session, order_id: uuid.UUID) -> Order:
    return db.query(Order).filter(Order.id == order_id).first()

def get_order_by_number(db: Session, order_number: str) -> Order:
    return db.query(Order).filter(Order.order_number == order_number).first()

def get_user_orders(db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 20):
    return db.query(Order).filter(
        Order.user_id == user_id
    ).order_by(
        Order.created_at.desc()
    ).offset(skip).limit(limit).all()

def get_guest_orders(db: Session, session_id: str, skip: int = 0, limit: int = 20):
    return db.query(Order).filter(
        Order.session_id == session_id
    ).order_by(
        Order.created_at.desc()
    ).offset(skip).limit(limit).all()