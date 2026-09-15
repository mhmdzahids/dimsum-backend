from flask import Blueprint, request
import re
from app.shared.response import api_success, api_error
from app.modules.auth.service import AuthService
from app.core.security import login_required
from app.core.limiter import limiter

auth_bp = Blueprint('auth', __name__)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.get_json()
    if not data:
        return api_error('Invalid request body', 400)
        
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''
    full_name = (data.get('full_name') or '').strip()
    
    if not all([email, password, full_name]):
        return api_error('Missing required fields: email, password, full_name', 400)
        
    if not EMAIL_REGEX.match(email):
        return api_error('Invalid email format', 400)
        
    if len(password) < 6:
        return api_error('Password must be at least 6 characters', 400)
        
    try:
        user = AuthService.register(email, password, full_name)
        return api_success(data=user.to_dict(), status=201, message='User registered successfully')
    except ValueError as e:
        return api_error(str(e), 400)

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    if not data:
        return api_error('Invalid request body', 400)
        
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''
    
    if not all([email, password]):
        return api_error('Missing required fields: email, password', 400)
        
    try:
        user, token = AuthService.login(email, password)
        return api_success(data={
            'user': user.to_dict(),
            'token': token
        }, message='Login successful')
    except ValueError as e:
        return api_error(str(e), 401)

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    # Revoke current bearer token
    token = getattr(request, 'token', None)
    if token:
        AuthService.revoke_token(token)
    return api_success(message='Logged out successfully')

@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    from app.modules.auth.models import User
    from app.core.db import db_session
    
    user = db_session.query(User).get(request.user_id)
    if not user:
        return api_error('User not found', 404)
        
    return api_success(data=user.to_dict())
