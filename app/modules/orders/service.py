import html
import secrets
from app.core.db import db_session
from app.modules.orders.models import Order, OrderItem
from app.modules.payments.models import Payment
from app.modules.payments.service import PaywuzService
from app.modules.products.models import Product
from app.modules.inventory.models import InventoryTransaction
from app.shared.utils import utc_now

DEFAULT_PACKAGING_FEE = 5000.0

class OrderService:
    @staticmethod
    def get_by_id(order_id: str):
        return db_session.query(Order).get(order_id)

    @classmethod
    def create_order(cls, customer_data: dict, items: list):
        from app.modules.auth.models import User
        from app.modules.auth.service import AuthService
        
        email = (customer_data.get('email') or '').strip()
        phone = (customer_data.get('phone') or '').strip()
        raw_name = (customer_data.get('name') or 'Guest').strip()
        name = html.escape(raw_name, quote=True)
        
        identifier = phone if phone else email
        if not identifier:
            raise ValueError("Phone or Email is required for checkout")
            
        customer = db_session.query(User).filter((User.email == identifier) | (User.email == email)).first()
        if not customer:
            # Generate unmatchable secure random hash for guest
            random_pw = secrets.token_hex(24)
            customer = User(
                email=identifier,
                password_hash=AuthService.hash_password(random_pw),
                full_name=name,
                role='customer'
            )
            db_session.add(customer)
            db_session.flush()

        # Fixed server-calculated packaging fee (never trusted from client)
        total_amount = DEFAULT_PACKAGING_FEE
        order_items_to_add = []
        
        for item in items:
            product_id = item.get('product_id')
            product = db_session.query(Product).get(product_id)
            if not product:
                raise ValueError(f"Product {product_id} not found")
            if not product.is_active:
                raise ValueError(f"Product '{product.name}' is currently not available")
            
            try:
                qty = int(item.get('quantity', 0))
            except (ValueError, TypeError):
                raise ValueError(f"Invalid quantity for {product.name}")
                
            if qty <= 0:
                raise ValueError(f"Quantity for {product.name} must be greater than 0")
            if qty > 500:
                raise ValueError(f"Quantity for {product.name} exceeds maximum limit")
            if product.stock_qty < qty:
                raise ValueError(f"Insufficient stock for '{product.name}'. Available: {product.stock_qty}")
                
            unit_price = float(product.price)
            total_amount += unit_price * qty
            
            order_items_to_add.append(OrderItem(
                product_id=product.id,
                quantity=qty,
                unit_price=unit_price
            ))
            
        new_order = Order(
            customer_id=customer.id,
            total_amount=total_amount,
            status='pending_payment'
        )
        
        db_session.add(new_order)
        db_session.flush()
        
        for oi in order_items_to_add:
            oi.order_id = new_order.id
            db_session.add(oi)
            
        # Create Paywuz QRIS
        try:
            paywuz_res = PaywuzService.create_qris_transaction(new_order.id, total_amount)
            
            payment_record = Payment(
                order_id=new_order.id,
                gateway='paywuz',
                gateway_ref_id=paywuz_res.get('id'),
                status='pending'
            )
            db_session.add(payment_record)
            db_session.commit()
            
            return new_order, paywuz_res
            
        except Exception as e:
            db_session.rollback()
            raise e

    @classmethod
    def handle_payment_webhook(cls, order_id: str, status: str, payload: dict):
        order = cls.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
            
        payment = db_session.query(Payment).filter_by(order_id=order_id).first()
        if not payment:
            raise ValueError("Payment record not found")
            
        payment.raw_webhook_payload = payload
        
        if payment.status == 'success':
            return order
            
        if status.lower() in ['success', 'settlement']:
            payment.status = 'success'
            order.status = 'paid'
            order.paid_at = utc_now()
            # 256-bit cryptographically secure random token (43 chars)
            order.qr_token = secrets.token_urlsafe(32)
            
        elif status.lower() in ['failed', 'expired', 'cancelled']:
            payment.status = 'failed'
            order.status = 'cancelled'
            
        db_session.commit()
        return order

    @classmethod
    def verify_and_complete_pickup(cls, qr_token: str, staff_user_id: str):
        """
        Atomic verification by cashier: validates QR token, applies SELECT FOR UPDATE
        row lock to deduct stock and logs inventory transaction in a single DB transaction.
        """
        if not qr_token or len(qr_token) < 16:
            raise ValueError("Invalid QR token provided")
            
        order = db_session.query(Order).filter(
            Order.qr_token == qr_token,
            Order.status == 'paid'
        ).first()
        
        if not order:
            raise ValueError("Invalid QR code or order has already been completed")
            
        try:
            order.status = 'completed'
            order.completed_at = utc_now()
            
            for item in order.items:
                # Row-level lock on product
                product = db_session.query(Product).with_for_update().get(item.product_id)
                if not product:
                    raise ValueError(f"Product {item.product_id} no longer exists")
                    
                if product.stock_qty < item.quantity:
                    raise ValueError(f"Insufficient stock for {product.name} to complete order")
                    
                product.stock_qty -= item.quantity
                
                db_session.add(InventoryTransaction(
                    product_id=product.id,
                    type='out',
                    quantity=item.quantity,
                    reference_type='order',
                    reference_id=order.id,
                    created_by=staff_user_id
                ))
                
            db_session.commit()
            return order
        except Exception:
            db_session.rollback()
            raise
