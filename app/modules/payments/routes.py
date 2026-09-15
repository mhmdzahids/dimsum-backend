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

    # 1. Check X-Paywuz-Signature, X-Webhook-Signature, or X-Signature header (HMAC SHA256)
    received_sig = headers.get('X-Paywuz-Signature') or headers.get('X-Webhook-Signature') or headers.get('X-Signature')
    if received_sig:
        expected_sig = hmac.new(secret.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()
        if hmac.compare_digest(expected_sig, received_sig):
            return True

    # 2. Check Authorization Bearer token
    auth_header = headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        if hmac.compare_digest(secret, token):
            return True

    # 3. Check X-Webhook-Secret, X-Api-Key, or X-Paywuz-Secret header
    secret_header = headers.get('X-Webhook-Secret') or headers.get('X-Api-Key') or headers.get('X-Paywuz-Secret')
    if secret_header and hmac.compare_digest(secret, secret_header):
        return True

    # 4. In development, allow if neither is provided
    if Config.ENV == 'development':
        return True

    return False

@payments_bp.route('/webhook', methods=['POST'])
@limiter.limit("60 per minute")
def handle_webhook():
    from app.modules.payments.service import PaywuzService

    raw_data = request.get_data()
    payload = request.get_json(silent=True) or {}
    logger.info(f"Paywuz webhook received. Headers: {dict(request.headers)}, Payload: {payload}")

    data = payload.get('data', payload) if isinstance(payload, dict) else {}
    
    # Extract order identifier or transaction ID
    identifier = (
        data.get('orderId') or 
        data.get('order_id') or 
        payload.get('orderId') or 
        payload.get('order_id') or 
        data.get('id') or 
        payload.get('id') or 
        data.get('transaction_id')
    )
    status = data.get('status') or payload.get('status')
    
    # 1. Verify via Signature if present
    is_verified = verify_webhook_signature(raw_data, request.headers)

    # 2. Fallback: If signature header is absent or secret is mismatched,
    # verify directly via authenticated Paywuz API call (server-to-server inquiry)
    if not is_verified and identifier:
        tx_id = data.get('id') or payload.get('id') or identifier
        tx_verified = PaywuzService.get_transaction(tx_id)
        if tx_verified and tx_verified.get('status'):
            logger.info(f"Webhook authenticated via Paywuz API inquiry for tx {tx_id}")
            is_verified = True
            status = tx_verified.get('status')
            identifier = tx_verified.get('orderId') or identifier

    if not is_verified:
        logger.warning(f"Unauthorized webhook rejected: signature invalid and API inquiry failed.")
        return api_error('Invalid webhook signature', 403)

    if not identifier:
        return api_error('Missing order or transaction identifier in payload', 400)
        
    # 3. Process Webhook atomically
    try:
        OrderService.handle_payment_webhook(identifier, status, payload)
        return api_success(message='Webhook processed successfully')
    except ValueError as ve:
        logger.warning(f"Webhook processing error for identifier {identifier}: {str(ve)}")
        return api_error(str(ve), 400)
    except Exception as e:
        logger.exception(f"Unexpected error processing webhook for identifier {identifier}")
        return api_error('Internal server error during webhook processing', 500)
