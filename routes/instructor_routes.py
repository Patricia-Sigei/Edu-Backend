from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Assignment, Lesson, User
from schemas import assignment_schema, assignments_schema, lesson_schema, lessons_schema

instructor_bp = Blueprint('instructor', __name__, url_prefix='/api/instructor')

@instructor_bp.route('/dashboard')
@jwt_required()
def dashboard():
    try:
        current_user_id = get_jwt_identity()
        instructor = User.query.get(current_user_id)
        
        if not instructor or instructor.role != 'INSTRUCTOR':
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        assignments = Assignment.query.filter_by(instructor_id=current_user_id).all()
        
        return jsonify({
            'status': 'success',
            'data': assignments_schema.dump(assignments)
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@instructor_bp.route('/lesson', methods=['POST'])
@jwt_required()
def create_lesson():
    try:
        current_user_id = get_jwt_identity()
        instructor = User.query.get(current_user_id)
        
        if not instructor or instructor.role != 'INSTRUCTOR':
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('content'):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields'
            }), 400

        new_lesson = Lesson(
            title=data['title'],
            content=data['content'],
            description=data.get('description'),
            due_date=data.get('due_date'),
            instructor_id=current_user_id
        )
        db.session.add(new_lesson)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Lesson created successfully',
            'data': lesson_schema.dump(new_lesson)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@instructor_bp.route('/assignment', methods=['POST'])
@jwt_required()
def create_assignment():
    try:
        current_user_id = get_jwt_identity()
        instructor = User.query.get(current_user_id)
        
        if not instructor or instructor.role != 'INSTRUCTOR':
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('description') or not data.get('due_date'):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields'
            }), 400

        new_assignment = Assignment(
            title=data['title'],
            description=data['description'],
            due_date=data['due_date'],
            instructor_id=current_user_id,
            status='pending'
        )
        db.session.add(new_assignment)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Assignment created successfully',
            'data': assignment_schema.dump(new_assignment)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@instructor_bp.route('/assignment/<int:assignment_id>/grade', methods=['PUT'])
@jwt_required()
def grade_assignment(assignment_id):
    try:
        current_user_id = get_jwt_identity()
        instructor = User.query.get(current_user_id)
        
        if not instructor or instructor.role != 'INSTRUCTOR':
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        data = request.get_json()
        
        if not data or 'grade' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing grade data'
            }), 400

        assignment = Assignment.query.get_or_404(assignment_id)
        
        if assignment.instructor_id != current_user_id:
            return jsonify({
                'status': 'error',
                'message': 'You can only grade your own assignments'
            }), 403

        assignment.grade = data['grade']
        assignment.status = 'graded'
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Assignment graded successfully',
            'data': assignment_schema.dump(assignment)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Additional routes for getting instructor's lessons and assignments
@instructor_bp.route('/lessons')
@jwt_required()
def get_lessons():
    try:
        current_user_id = get_jwt_identity()
        instructor = User.query.get(current_user_id)
        
        if not instructor or instructor.role != 'INSTRUCTOR':
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        lessons = Lesson.query.filter_by(instructor_id=current_user_id).all()
        
        return jsonify({
            'status': 'success',
            'data': lessons_schema.dump(lessons)
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500