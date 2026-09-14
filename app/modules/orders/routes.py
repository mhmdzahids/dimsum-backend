from flask import Blueprint, request
from app.shared.response import api_success, api_error
from app.modules.orders.service import OrderService
from app.core.security import login_required

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('', methods=['POST'])
def create_order():
    data = request.get_json()
    if not data or not data.get('items') or not data.get('customer'):
        return api_error('Invalid request body or missing items/customer info', 400)
        
    try:
        # In service, we will handle finding or creating the user
        order, paywuz_res = OrderService.create_order(
            customer_data=data['customer'],
            items=data['items'],
            other_fees=float(data.get('other_fees', 5000))
        )
        return api_success(data={
            'order': order.to_dict(),
            'paywuz': paywuz_res
        }, status=201, message='Order created successfully')
    except ValueError as e:
        return api_error(str(e), 400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return api_error(f'Internal server error during order creation: {str(e)}', 500)

@orders_bp.route('/<order_id>', methods=['GET'])
def get_order(order_id):
    order = OrderService.get_by_id(order_id)
    if not order:
        return api_error('Order not found', 404)
    return api_success(data=order.to_dict())
