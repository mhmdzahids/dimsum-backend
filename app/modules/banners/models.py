from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.core.db import Base
from app.shared.models import SerializableMixin
import uuid

class Banner(Base, SerializableMixin):
    __tablename__ = 'banners'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    image_url = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
