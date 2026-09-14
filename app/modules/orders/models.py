from sqlalchemy import Column, String, Numeric, Integer, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.shared.models import SerializableMixin
from app.shared.utils import utc_now, generate_uuid

class Order(Base, SerializableMixin):
    __tablename__ = 'orders'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    customer_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    status = Column(Enum('pending_payment', 'paid', 'fulfilling', 'completed', 'cancelled', name='order_status'), default='pending_payment', nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    qr_token = Column(String(64), unique=True, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    paid_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False)

class OrderItem(Base, SerializableMixin):
    __tablename__ = 'order_items'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey('orders.id'), nullable=False)
    product_id = Column(String(36), ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    
    order = relationship("Order", back_populates="items")
