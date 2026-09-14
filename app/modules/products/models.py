from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime
from app.core.db import Base
from app.shared.models import SerializableMixin
from app.shared.utils import utc_now, generate_uuid

class Product(Base, SerializableMixin):
    __tablename__ = 'products'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    weight = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    price = Column(Numeric(12, 2), nullable=False)
    sku = Column(String(64), unique=True, nullable=False)
    image_url = Column(String(500), nullable=True)
    stock_qty = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
