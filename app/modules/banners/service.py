import os
from werkzeug.utils import secure_filename
import uuid
from app.core.db import db_session
from app.modules.banners.models import Banner
from app.core.config import Config

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class BannerService:
    @staticmethod
    def get_all(active_only=False):
        query = db_session.query(Banner)
        if active_only:
            query = query.filter(Banner.is_active == True)
        return query.order_by(Banner.created_at.desc()).all()
        
    @staticmethod
    def get_by_id(banner_id):
        return db_session.query(Banner).filter(Banner.id == banner_id).first()
        
    @staticmethod
    def save_banner(file):
        if not file or file.filename == '':
            raise ValueError("No file provided")
            
        if not allowed_file(file.filename):
            raise ValueError("File type not allowed. Supported formats: png, jpg, jpeg, webp")
            
        filename = secure_filename(file.filename)
        # Add random uuid to prevent overwriting
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Ensure upload folder exists
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        file_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Determine URL
        # For simplicity, we assume /static/uploads/banners/filename
        # Because we will serve it from the static folder
        image_url = f"/static/uploads/banners/{unique_filename}"
        
        banner = Banner(
            filename=unique_filename,
            image_url=image_url,
            is_active=True
        )
        
        db_session.add(banner)
        db_session.commit()
        return banner
        
    @staticmethod
    def delete(banner_id):
        banner = BannerService.get_by_id(banner_id)
        if not banner:
            raise ValueError("Banner not found")
            
        # Delete file if it exists
        file_path = os.path.join(Config.UPLOAD_FOLDER, banner.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        db_session.delete(banner)
        db_session.commit()
