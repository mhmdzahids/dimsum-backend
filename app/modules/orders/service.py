from app.core.db import db_session
from app.modules.orders.models import Order, OrderItem
from app.modules.payments.models import Payment
from app.modules.payments.service import PaywuzService
from app.modules.products.models import Product

class OrderService:
    @staticmethod
    def get_by_id(order_id: str):
        return db_session.query(Order).get(order_id)

    @classmethod
    def create_order(cls, customer_data: dict, items: list, other_fees: float = 5000):
        # Handle guest customer
        from app.modules.auth.models import User
        
        email = customer_data.get('email')
        phone = customer_data.get('phone')
        name = customer_data.get('name', 'Guest')
        
        # Dimsum typically requires phone, we'll use phone or email as identifier
        identifier = phone if phone else email
        if not identifier:
            raise ValueError("Phone or Email is required for guest checkout")
            
        customer = db_session.query(User).filter((User.email == identifier) | (User.email == email)).first()
        if not customer:
            customer = User(
                email=identifier, # store phone as email if email is empty for dummy purposes
                password_hash='guest',
                full_name=name,
                role='customer'
            )
            db_session.add(customer)
            db_session.flush()

        # Calculate total and validate items
        total_amount = other_fees
        order_items_to_add = []
        
        for item in items:
            product = db_session.query(Product).get(item['product_id'])
            if not product:
                raise ValueError(f"Product {item['product_id']} not found")
            
            qty = int(item['quantity'])
            if qty <= 0:
                raise ValueError("Quantity must be greater than 0")
                
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
        db_session.flush() # Get order ID before generating payment
        
        for oi in order_items_to_add:
            oi.order_id = new_order.id
            db_session.add(oi)
            
        # Create Paywuz QRIS
        try:
            paywuz_res = PaywuzService.create_qris_transaction(new_order.id, total_amount)
            
            # Save to payments table
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
        
        # Depending on Paywuz webhook structure, let's assume status 'success' or 'settlement' means paid
        if status.lower() in ['success', 'settlement']:
            payment.status = 'success'
            order.status = 'paid'
            # Here we could generate qr_token as per spec
            from app.shared.utils import generate_uuid
            import uuid
            order.qr_token = str(uuid.uuid4())[:8] # Short token
            
        elif status.lower() == 'failed' or status.lower() == 'expired':
            payment.status = 'failed'
            order.status = 'cancelled'
            
        db_session.commit()
        return order
