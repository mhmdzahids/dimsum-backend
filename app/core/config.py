import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///dimsum_dev.db')
    
    ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
    
    PAYWUZ_API_KEY = os.environ.get('PAYWUZ_API_KEY', '')
    PAYWUZ_API_URL = os.environ.get('PAYWUZ_API_URL', 'https://api.paywuz.id/v1')
    PAYWUZ_WEBHOOK_SECRET = os.environ.get('PAYWUZ_WEBHOOK_SECRET', '')
    
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join('app', 'static', 'uploads', 'banners'))
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024 # 5 MB limit

    # Fail fast if in production and secrets are insecure
    ENV = os.environ.get('FLASK_ENV', 'development')
    if ENV == 'production':
        if SECRET_KEY in ('default-secret-key', 'super-secret-dev-key-change-in-prod') or len(SECRET_KEY) < 32:
            raise RuntimeError("CRITICAL: Insecure SECRET_KEY configured for production!")
        if not PAYWUZ_WEBHOOK_SECRET:
            raise RuntimeError("CRITICAL: PAYWUZ_WEBHOOK_SECRET must be set in production!")
