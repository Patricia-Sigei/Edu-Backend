from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Assignment, Lesson, User  
from schemas import assignment_schema, assignments_schema, lesson_schema, lessons_schema

student_bp = Blueprint('student', __name__, url_prefix='/api/student')

@student_bp.route('/dashboard')
@jwt_required()
def dashboard():
    try:
        current_user_id = get_jwt_identity()
        student = User.query.get(current_user_id)
        
        if not student or not student.is_student():  
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        # Get assignments assigned to this student
        assignments = Assignment.query.filter(
            (Assignment.student_id == None) |  
            (Assignment.student_id == current_user_id)  
        ).all()

        # Get lessons for this student
        lessons = student.student_lessons

        return jsonify({
            'status': 'success',
            'data': {
                'assignments': assignments_schema.dump(assignments),
                'lessons': lessons_schema.dump(lessons)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
# route for submitting assignment 
@student_bp.route('/assignment/<int:assignment_id>/submit', methods=['POST'])
@jwt_required()
def submit_assignment(assignment_id):
    try:
        current_user_id = get_jwt_identity()
        student = User.query.get(current_user_id)
        
        if not student or not student.is_student():  
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        assignment = Assignment.query.get_or_404(assignment_id)
        data = request.get_json()

        if not data or 'submission' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing submission data'
            }), 400

        
        assignment.submit(student.id, data['submission'])
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Assignment submitted successfully',
            'data': assignment_schema.dump(assignment)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
# route for viewing student lessons
@student_bp.route('/lessons')
@jwt_required()
def view_lessons():
    try:
        current_user_id = get_jwt_identity()
        student = User.query.get(current_user_id)
        
        if not student or not student.is_student():  
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        lessons = student.student_lessons.all()
        
        return jsonify({
            'status': 'success',
            'data': lessons_schema.dump(lessons)
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
# route for viewing the assignments
@student_bp.route('/my-assignments')
@jwt_required()
def my_assignments():
    try:
        current_user_id = get_jwt_identity()
        student = User.query.get(current_user_id)
        
        if not student or not student.is_student():  
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        # Get assignments submitted by this student
        assignments = student.student_assignments  
        
        return jsonify({
            'status': 'success',
            'data': assignments_schema.dump(assignments)
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# New route to enroll in a lesson
@student_bp.route('/lesson/<int:lesson_id>/enroll', methods=['POST'])
@jwt_required()
def enroll_lesson(lesson_id):
    try:
        current_user_id = get_jwt_identity()
        student = User.query.get(current_user_id)
        
        if not student or not student.is_student():
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access'
            }), 403

        lesson = Lesson.query.get_or_404(lesson_id)
        lesson.add_student(student) 
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Enrolled in lesson successfully',
            'data': lesson_schema.dump(lesson)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500