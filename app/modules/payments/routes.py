from flask import Blueprint, request
from app.shared.response import api_success, api_error
from app.modules.orders.service import OrderService

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    payload = request.get_json()
    if not payload:
        return api_error('Invalid webhook payload', 400)
        
    # Since we don't have the exact structure of the webhook payload,
    # we'll assume it resembles the response object or contains status and orderId.
    # Typically it's payload['data']['status'] and payload['data']['orderId']
    
    data = payload.get('data', payload)
    
    order_id = data.get('orderId')
    status = data.get('status')
    
    if not order_id or not status:
        # Some webhooks use 'id' or different formats, but based on Paywuz docs, 
        # it returns orderId.
        return api_error('Missing orderId or status in payload', 400)
        
    try:
        OrderService.handle_payment_webhook(order_id, status, payload)
        return api_success(message='Webhook processed successfully')
    except Exception as e:
        # It's important to return 200/Success to Paywuz even if our internal logic fails,
        # otherwise they might retry infinitely. But for debugging, we return 400.
        return api_error(str(e), 400)
