import re
import logging
from flask import Blueprint, request
from app.shared.response import api_success, api_error
from app.modules.orders.service import OrderService
from app.core.security import admin_required
from app.core.limiter import limiter

logger = logging.getLogger(__name__)
orders_bp = Blueprint('orders', __name__)

UUID_REGEX = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)

@orders_bp.route('', methods=['POST'])
@limiter.limit("20 per minute")
def create_order():
    data = request.get_json(silent=True)
    if not data or not data.get('items') or not data.get('customer'):
        return api_error('Invalid request body or missing items/customer info', 400)
        
    try:
        # Note: packaging fee is calculated exclusively on the server in OrderService
        order, paywuz_res = OrderService.create_order(
            customer_data=data['customer'],
            items=data['items']
        )
        return api_success(data={
            'order': order.to_dict(),
            'paywuz': paywuz_res
        }, status=201, message='Order created successfully')
    except ValueError as e:
        return api_error(str(e), 400)
    except Exception as e:
        logger.exception("Internal error during order creation")
        return api_error('Internal server error during order creation. Please try again later.', 500)

@orders_bp.route('/<order_id>', methods=['GET'])
@limiter.limit("40 per minute")
def get_order(order_id):
    if not UUID_REGEX.match(order_id):
        return api_error('Invalid order ID format', 400)
        
    order = OrderService.get_by_id(order_id)
    if not order:
        return api_error('Order not found', 404)
        
    return api_success(data=order.to_dict())

@orders_bp.route('/verify', methods=['POST'])
@admin_required
@limiter.limit("10 per minute")
def verify_pickup():
    data = request.get_json(silent=True) or {}
    qr_token = (data.get('qr_token') or '').strip()
    if not qr_token:
        return api_error('QR token is required', 400)
        
    try:
        staff_id = getattr(request, 'user_id', None)
        order = OrderService.verify_and_complete_pickup(qr_token, staff_id)
        return api_success(data=order.to_dict(), message='Order verified and marked as completed')
    except ValueError as ve:
        return api_error(str(ve), 400)
    except Exception:
        logger.exception("Error during pickup verification")
        return api_error('Internal error during pickup verification', 500)
