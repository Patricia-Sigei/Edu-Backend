from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from models import db, User
from schemas import user_schema, users_schema

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        current_user_id = get_jwt_identity()
        admin = User.query.get(current_user_id)
        
        if not admin or admin.role != 'ADMIN':
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        users = User.query.all()
        return jsonify({
            'status': 'success',
            'data': users_schema.dump(users)
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@admin_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    try:
        current_user_id = get_jwt_identity()
        admin = User.query.get(current_user_id)
        
        if not admin or admin.role != 'ADMIN':
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        data = request.get_json()
        
        if not data or not all(k in data for k in ['username', 'password', 'role']):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields'
            }), 400

        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'status': 'error',
                'message': 'Username already exists'
            }), 400

        hashed_password = generate_password_hash(data['password'])
        new_user = User(
            username=data['username'],
            password=hashed_password,
            role=data['role']
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'User created successfully',
            'data': user_schema.dump(new_user)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        admin = User.query.get(current_user_id)
        
        if not admin or admin.role != 'ADMIN':
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        user = User.query.get_or_404(user_id)
        data = request.get_json()

        if 'username' in data:
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({
                    'status': 'error',
                    'message': 'Username already exists'
                }), 400
            user.username = data['username']
            
        if 'password' in data and data['password']:
            user.password = generate_password_hash(data['password'])
            
        if 'role' in data:
            user.role = data['role']

        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'User updated successfully',
            'data': user_schema.dump(user)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        admin = User.query.get(current_user_id)
        
        if not admin or admin.role != 'ADMIN':
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        user = User.query.get_or_404(user_id)
        
        if user.id == current_user_id:
            return jsonify({
                'status': 'error',
                'message': 'Cannot delete your own account'
            }), 400

        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'User {user.username} deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500