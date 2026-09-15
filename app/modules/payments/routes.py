import hmac
import hashlib
import logging
from flask import Blueprint, request, jsonify
from app.shared.response import api_success, api_error
from app.modules.orders.service import OrderService
from app.modules.payments.models import Payment
from app.core.config import Config
from app.core.limiter import limiter
from app.core.db import db_session

logger = logging.getLogger(__name__)
payments_bp = Blueprint('payments', __name__)

def verify_webhook_signature(raw_body: bytes, headers: dict) -> bool:
    secret = Config.PAYWUZ_WEBHOOK_SECRET or Config.PAYWUZ_API_KEY
    if not secret:
        # In development if secret is not set, allow with warning
        if Config.ENV == 'development':
            logger.warning("PAYWUZ_WEBHOOK_SECRET not set in development. Skipping strict signature check.")
            return True
        return False

    # 1. Check X-Webhook-Signature or X-Signature header (HMAC SHA256)
    received_sig = headers.get('X-Webhook-Signature') or headers.get('X-Signature')
    if received_sig:
        expected_sig = hmac.new(secret.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_sig, received_sig)

    # 2. Check Authorization Bearer token
    auth_header = headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        return hmac.compare_digest(secret, token)

    # 3. Check X-Webhook-Secret or X-Api-Key header
    secret_header = headers.get('X-Webhook-Secret') or headers.get('X-Api-Key')
    if secret_header:
        return hmac.compare_digest(secret, secret_header)

    # 4. In development, allow if neither is provided
    if Config.ENV == 'development':
        return True

    return False

@payments_bp.route('/webhook', methods=['POST'])
@limiter.limit("30 per minute")
def handle_webhook():
    # 1. Verify Signature
    if not verify_webhook_signature(request.get_data(), request.headers):
        logger.warning("Unauthorized webhook request attempt: invalid signature")
        return api_error('Invalid webhook signature', 403)

    payload = request.get_json(silent=True)
    if not payload:
        return api_error('Invalid webhook payload format', 400)
        
    data = payload.get('data', payload)
    order_id = data.get('orderId')
    status = data.get('status')
    
    if not order_id or not status:
        return api_error('Missing orderId or status in payload', 400)
        
    # 2. Idempotency Check: Don't reprocess if already successfully settled
    existing_payment = db_session.query(Payment).filter_by(order_id=order_id).first()
    if existing_payment and existing_payment.status == 'success':
        logger.info(f"Webhook received for already settled order {order_id}. Returning 200 OK.")
        return jsonify({'success': True, 'status': 'already_processed'}), 200

    # 3. Process Webhook
    try:
        OrderService.handle_payment_webhook(order_id, status, payload)
        return api_success(message='Webhook processed successfully')
    except ValueError as ve:
        logger.warning(f"Webhook processing error for order {order_id}: {str(ve)}")
        return api_error(str(ve), 400)
    except Exception as e:
        logger.exception(f"Unexpected error processing webhook for order {order_id}")
        return api_error('Internal server error during webhook processing', 500)
