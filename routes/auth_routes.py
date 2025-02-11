import re
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, db
from schemas import user_schema

auth_bp = Blueprint('auth', __name__)

# validation for new password after being assigned a default password
def is_valid_password(password):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(pattern, password) is not None
# login route
@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'status': 'error', 'message': 'Missing username or password'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        if user and check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity=f"{user.id}", additional_claims={'role': user.role})
            return jsonify({'status': 'success', 'message': 'Login successful', 'data': {'token': access_token, 'user': user_schema.dump(user)}}), 200
        
        return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
# token verfication route
@auth_bp.route('/api/auth/verify', methods=['GET'])
@jwt_required()
def verify_token():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        return jsonify({'status': 'success', 'data': {'user': user_schema.dump(user)}}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@auth_bp.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'status': 'success', 'message': 'Logged out successfully'}), 200
# password reset route
@auth_bp.route('/api/auth/reset-password', methods=['POST'])
@jwt_required()
def reset_password():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not data or not data.get('old_password') or not data.get('new_password'):
            return jsonify({'status': 'error', 'message': 'Missing password data'}), 400

        if not check_password_hash(user.password, data['old_password']):
            return jsonify({'status': 'error', 'message': 'Current password is incorrect'}), 401

        if not is_valid_password(data['new_password']):
            return jsonify({'status': 'error', 'message': 'New password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one number, and one special character'}), 400

        user.password = generate_password_hash(data['new_password'])
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Password updated successfully'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
