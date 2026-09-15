from flask import Blueprint, request
from app.shared.response import api_success, api_error
from app.modules.products.service import ProductService
from app.core.security import admin_required

products_bp = Blueprint('products', __name__)

@products_bp.route('', methods=['GET'])
def get_products():
    products = ProductService.get_all()
    return api_success(data=[p.to_dict() for p in products])

@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    product = ProductService.get_by_id(product_id)
    if not product:
        return api_error('Product not found', 404)
    return api_success(data=product.to_dict())

@products_bp.route('', methods=['POST'])
@admin_required
def create_product():
    data = request.get_json()
    if not data:
        return api_error('Invalid request body', 400)
        
    required_fields = ['name', 'price', 'sku']
    if not all(field in data for field in required_fields):
        return api_error(f'Missing required fields: {", ".join(required_fields)}', 400)
        
    try:
        product = ProductService.create(
            name=data.get('name'),
            price=float(data.get('price')),
            sku=data.get('sku'),
            category=data.get('category'),
            is_active=data.get('is_active', True),
            stock_qty=int(data.get('stock_qty', 0))
        )
        return api_success(data=product.to_dict(), status=201, message='Product created successfully')
    except ValueError as e:
        return api_error(str(e), 400)
    except Exception as e:
        return api_error('Invalid data types', 400)

@products_bp.route('/<product_id>/image', methods=['POST'])
@admin_required
def upload_product_image(product_id):
    if 'image' not in request.files:
        return api_error('No image file provided', 400)
        
    file = request.files['image']
    try:
        product = ProductService.save_image(product_id, file)
        return api_success(data=product.to_dict(), status=200, message='Product image uploaded successfully')
    except ValueError as e:
        if str(e) == "Product not found":
            return api_error(str(e), 404)
        return api_error(str(e), 400)
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception("Product image upload failed")
        return api_error('Upload failed due to an internal server error', 500)

@products_bp.route('/<product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    data = request.get_json()
    if not data:
        return api_error('Invalid request body', 400)
        
    try:
        product = ProductService.update(product_id, **data)
        return api_success(data=product.to_dict(), message='Product updated successfully')
    except ValueError as e:
        if str(e) == "Product not found":
            return api_error(str(e), 404)
        return api_error(str(e), 400)

@products_bp.route('/<product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    try:
        ProductService.delete(product_id)
        return api_success(message='Product deleted successfully')
    except ValueError as e:
        return api_error(str(e), 404)
