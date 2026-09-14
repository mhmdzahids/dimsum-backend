from sqlalchemy import Column, String, Enum, DateTime
from app.core.db import Base
from app.shared.models import SerializableMixin
from app.shared.utils import utc_now, generate_uuid

class User(Base, SerializableMixin):
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum('customer', 'admin', name='user_roles'), default='customer', nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    def to_dict(self, **kwargs):
        # NEVER expose password_hash
        return super().to_dict(exclude={'password_hash'})
