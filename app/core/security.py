import jwt
from functools import wraps
from flask import request, jsonify
from app.core.config import Config

def verify_token(token):
    try:
        decoded = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({'success': False, 'error': 'Token is missing'}), 401
            
        decoded = verify_token(token)
        if not decoded:
            return jsonify({'success': False, 'error': 'Token is invalid or expired'}), 401
            
        request.user_id = decoded.get("user_id")
        request.user_role = decoded.get("role")
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
        if not token:
            return jsonify({'success': False, 'error': 'Token is missing'}), 401
            
        decoded = verify_token(token)
        if not decoded:
            return jsonify({'success': False, 'error': 'Token is invalid or expired'}), 401
            
        if decoded.get("role") != "admin":
            return jsonify({'success': False, 'error': 'Admin privileges required'}), 403
            
        request.user_id = decoded.get("user_id")
        request.user_role = decoded.get("role")
        return f(*args, **kwargs)
    return decorated
