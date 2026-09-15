import jwt
from functools import wraps
from flask import request, jsonify
from app.core.config import Config

# In-memory blacklist for single-process hosting (cPanel / Gunicorn)
# In high-concurrency multi-worker clusters, this can be mapped to a DB table
blacklisted_tokens = set()

def revoke_token(token: str):
    if token:
        blacklisted_tokens.add(token)

def is_token_revoked(token: str) -> bool:
    return token in blacklisted_tokens

def verify_token(token):
    if not token or is_token_revoked(token):
        return None
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
            return jsonify({'success': False, 'error': 'Token is invalid, expired, or revoked'}), 401
            
        request.token = token
        request.user_id = decoded.get("user_id") or decoded.get("sub")
        request.user_role = decoded.get("role")
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if getattr(request, 'user_role', None) != "admin":
            return jsonify({'success': False, 'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated
