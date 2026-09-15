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

    # Environment
    ENV = os.environ.get('FLASK_ENV', 'development')

    # If in production and secrets are not provided, warn instead of crashing server boot
    if ENV == 'production':
        import logging
        _logger = logging.getLogger(__name__)
        if SECRET_KEY in ('default-secret-key', 'super-secret-dev-key-change-in-prod') or len(SECRET_KEY) < 32:
            _logger.warning("SECURITY WARNING: Insecure or default SECRET_KEY in production! Please set SECRET_KEY in environment variables.")
        if not PAYWUZ_WEBHOOK_SECRET:
            _logger.warning("SECURITY WARNING: PAYWUZ_WEBHOOK_SECRET is not set in production. Webhooks will be rejected until set.")
