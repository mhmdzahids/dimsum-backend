from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.core.db import db_session
from app.modules.auth.models import User
from app.core.config import Config

bcrypt = Bcrypt()

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.generate_password_hash(password).decode('utf-8')

    @staticmethod
    def check_password(password_hash: str, password: str) -> bool:
        return bcrypt.check_password_hash(password_hash, password)

    @staticmethod
    def generate_token(user_id: str, role: str) -> str:
        payload = {
            'user_id': user_id,
            'role': role,
            'exp': datetime.now(timezone.utc) + timedelta(days=7),
            'iat': datetime.now(timezone.utc)
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

    @classmethod
    def register(cls, email: str, password: str, full_name: str, role: str = 'customer'):
        existing_user = db_session.query(User).filter_by(email=email).first()
        if existing_user:
            raise ValueError('Email already registered')
            
        hashed_pw = cls.hash_password(password)
        new_user = User(
            email=email,
            password_hash=hashed_pw,
            full_name=full_name,
            role=role
        )
        db_session.add(new_user)
        db_session.commit()
        return new_user

    @classmethod
    def login(cls, email: str, password: str):
        user = db_session.query(User).filter_by(email=email).first()
        if not user or not cls.check_password(user.password_hash, password):
            raise ValueError('Invalid email or password')
            
        token = cls.generate_token(user.id, user.role)
        return user, token
