import logging
from flask import jsonify

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'success': False, 'error': str(e.description)}), 400
    
    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'success': False, 'error': 'Resource not found'}), 404
    
    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({'success': False, 'error': 'Too many requests'}), 429
    
    @app.errorhandler(Exception)
    def internal_error(e):
        logger.exception('Unhandled exception: %s', e)
        return jsonify({
            'success': False,
            'error': 'An internal error occurred'
        }), 500
