from sqlalchemy import Column, String, Integer, Enum, DateTime, ForeignKey
from app.core.db import Base
from app.shared.models import SerializableMixin
from app.shared.utils import utc_now, generate_uuid

class ProductionBatch(Base, SerializableMixin):
    __tablename__ = 'production_batches'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey('products.id'), nullable=False)
    batch_code = Column(String(64), unique=True, nullable=False)
    produced_qty = Column(Integer, nullable=False)
    remaining_qty = Column(Integer, nullable=False)
    produced_at = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    created_by = Column(String(36), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

class InventoryTransaction(Base, SerializableMixin):
    __tablename__ = 'inventory_transactions'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey('products.id'), nullable=False)
    batch_id = Column(String(36), ForeignKey('production_batches.id'), nullable=True)
    type = Column(Enum('in', 'out', 'adjustment', name='inventory_transaction_type'), nullable=False)
    quantity = Column(Integer, nullable=False)
    reference_type = Column(Enum('production', 'order', 'manual', name='inventory_reference_type'), nullable=False)
    reference_id = Column(String(36), nullable=True)
    created_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
