from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models import User, Assignment, Lesson

ma = Marshmallow()

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
        include_fk = True
        
    id = auto_field()
    username = auto_field()
    role = auto_field()
    
    
    # exclude to avoid circular imports by using strings for nested schemas
    assignments = ma.Nested('AssignmentSchema', many=True, exclude=('instructor', 'student'))
    student_assignments = ma.Nested('AssignmentSchema', many=True, exclude=('instructor', 'student'))
    lessons = ma.Nested('LessonSchema', many=True, exclude=('instructor', 'students'))
    student_lessons = ma.Nested('LessonSchema', many=True, exclude=('instructor', 'students'))

class AssignmentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Assignment
        include_relationships = True
        load_instance = True
        include_fk = True
        
    id = auto_field()
    title = auto_field()
    description = auto_field()
    due_date = auto_field()
    status = auto_field()
    grade = auto_field()
    submission = auto_field()
    
    # exclude to avoid circular nesting by excluding nested relationships
    instructor = ma.Nested('UserSchema', exclude=('assignments', 'student_assignments', 'lessons', 'student_lessons'))
    student = ma.Nested('UserSchema', exclude=('assignments', 'student_assignments', 'lessons', 'student_lessons'))

class LessonSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Lesson
        include_relationships = True
        load_instance = True
        include_fk = True
        
    id = auto_field()
    title = auto_field()
    content = auto_field()
    description = auto_field()
    due_date = auto_field()
    
    # exclude to avoid circular nesting by excluding nested relationships
    instructor = ma.Nested('UserSchema', exclude=('assignments', 'student_assignments', 'lessons', 'student_lessons'))
    students = ma.Nested('UserSchema', many=True, exclude=('assignments', 'student_assignments', 'lessons', 'student_lessons'))

# Schema instances
user_schema = UserSchema()
users_schema = UserSchema(many=True)

assignment_schema = AssignmentSchema()
assignments_schema = AssignmentSchema(many=True)

lesson_schema = LessonSchema()
lessons_schema = LessonSchema(many=True)