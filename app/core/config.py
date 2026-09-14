import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///dimsum_dev.db')
    
    ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
    
    PAYWUZ_API_KEY = os.environ.get('PAYWUZ_API_KEY', '')
    PAYWUZ_API_URL = os.environ.get('PAYWUZ_API_URL', 'https://api.paywuz.id/v1')
    
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join('app', 'static', 'uploads', 'banners'))
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024 # 5 MB limit
