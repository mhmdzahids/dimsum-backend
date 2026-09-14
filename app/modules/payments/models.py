from sqlalchemy import Column, String, Enum, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.shared.models import SerializableMixin
from app.shared.utils import utc_now, generate_uuid
from app.core.config import Config

# Fallback for SQLite JSON if needed, but SQLAlchemy handles JSON on SQLite usually
# We'll use SQLAlchemy's JSON type
class Payment(Base, SerializableMixin):
    __tablename__ = 'payments'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey('orders.id'), unique=True, nullable=False)
    gateway = Column(String(50), nullable=True)
    gateway_ref_id = Column(String(255), nullable=True)
    status = Column(Enum('pending', 'success', 'failed', name='payment_status'), default='pending', nullable=False)
    raw_webhook_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    
    order = relationship("Order", back_populates="payment")
