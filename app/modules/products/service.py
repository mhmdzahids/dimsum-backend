from app.core.db import db_session
from app.modules.products.models import Product

class ProductService:
    @staticmethod
    def get_all():
        return db_session.query(Product).all()

    @staticmethod
    def get_by_id(product_id: str):
        return db_session.query(Product).get(product_id)

    @staticmethod
    def get_by_sku(sku: str):
        return db_session.query(Product).filter_by(sku=sku).first()

    @classmethod
    def create(cls, name: str, price: float, sku: str, category: str = None, is_active: bool = True, stock_qty: int = 0):
        if cls.get_by_sku(sku):
            raise ValueError(f"Product with SKU '{sku}' already exists.")
            
        new_product = Product(
            name=name,
            price=price,
            sku=sku,
            category=category,
            is_active=is_active,
            stock_qty=stock_qty
        )
        db_session.add(new_product)
        db_session.commit()
        return new_product

    ALLOWED_UPDATE_FIELDS = {'name', 'description', 'weight', 'category', 'price', 'sku', 'image_url', 'is_active'}

    @classmethod
    def update(cls, product_id: str, **kwargs):
        import html
        product = cls.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
            
        if 'sku' in kwargs and kwargs['sku'] != product.sku:
            if cls.get_by_sku(kwargs['sku']):
                raise ValueError(f"Product with SKU '{kwargs['sku']}' already exists.")
                
        for key, value in kwargs.items():
            if key in cls.ALLOWED_UPDATE_FIELDS and hasattr(product, key):
                if isinstance(value, str) and key in {'name', 'description', 'weight', 'category'}:
                    value = html.escape(value.strip(), quote=True)
                setattr(product, key, value)
                
        db_session.commit()
        return product
    @classmethod
    def save_image(cls, product_id: str, file):
        import os
        from werkzeug.utils import secure_filename
        import uuid
        from app.core.config import Config
        
        product = cls.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")

        if not file or file.filename == '':
            raise ValueError("No file provided")
            
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
            raise ValueError("File type not allowed. Supported formats: png, jpg, jpeg, webp")
            
        filename = secure_filename(file.filename)
        unique_filename = f"prod_{uuid.uuid4().hex[:8]}_{filename}"
        
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        if product.image_url:
            old_filename = product.image_url.split('/')[-1]
            old_path = os.path.join(Config.UPLOAD_FOLDER, old_filename)
            if os.path.exists(old_path):
                os.remove(old_path)
        
        product.image_url = f"/static/uploads/banners/{unique_filename}"
        db_session.commit()
        return product

    @classmethod
    def delete(cls, product_id: str):
        product = cls.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
            
        db_session.delete(product)
        db_session.commit()
        return True
