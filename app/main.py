from flask import Flask
from flask_cors import CORS
from app.core.limiter import limiter
from app.core.config import Config
from app.core.db import init_db, teardown_session
from app.core.errors import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Extensions
    CORS(app, resources={r"/api/*": {
        "origins": Config.ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type", "X-Webhook-Signature"],
        "max_age": 3600
    }})
    limiter.init_app(app)
    
    # Database
    init_db(app)
    app.teardown_appcontext(teardown_session)
    
    # Error handlers
    register_error_handlers(app)
    
    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: https: blob:; "
            "connect-src 'self' https://api.paywuz.id;"
        )
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
    
    # Register blueprints
    from app.modules.auth.routes import auth_bp
    from app.modules.products.routes import products_bp
    from app.modules.orders.routes import orders_bp
    from app.modules.payments.routes import payments_bp
    from app.modules.banners.routes import banners_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(banners_bp, url_prefix='/api/banners')
    
    # Optional: A simple health check route
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'ok'}
        
    return app
