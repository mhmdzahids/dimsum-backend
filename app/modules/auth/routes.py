from flask import Blueprint, request
from app.shared.response import api_success, api_error
from app.modules.auth.service import AuthService
from app.core.security import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return api_error('Invalid request body', 400)
        
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    
    if not all([email, password, full_name]):
        return api_error('Missing required fields: email, password, full_name', 400)
        
    try:
        user = AuthService.register(email, password, full_name)
        return api_success(data=user.to_dict(), status=201, message='User registered successfully')
    except ValueError as e:
        return api_error(str(e), 400)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return api_error('Invalid request body', 400)
        
    email = data.get('email')
    password = data.get('password')
    
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

@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    # request.user_id is set by login_required decorator
    from app.modules.auth.models import User
    from app.core.db import db_session
    
    user = db_session.query(User).get(request.user_id)
    if not user:
        return api_error('User not found', 404)
        
    return api_success(data=user.to_dict())
