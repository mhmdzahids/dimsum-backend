from sqlalchemy import Column, String, Enum, DateTime, Text, ForeignKey
from app.core.db import Base
from app.shared.models import SerializableMixin
from app.shared.utils import utc_now, generate_uuid

class ChatMessage(Base, SerializableMixin):
    __tablename__ = 'chat_messages'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), nullable=False)
    sender_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    sender_role = Column(Enum('customer', 'admin', name='chat_sender_role'), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
