from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Association table for many-to-many relationship (Student-Lesson)
student_lessons = db.Table('student_lessons',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.id'), primary_key=True)
)

# User model
class User(db.Model):  # Removed UserMixin since we're using JWT
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    # Relationship: One-to-many with Assignment (Instructor)
    assignments = db.relationship('Assignment', back_populates='instructor', foreign_keys='Assignment.instructor_id', lazy=True)

    # Relationship: One-to-many with Assignment (Student)
    student_assignments = db.relationship('Assignment', back_populates='student', foreign_keys='Assignment.student_id', lazy=True)

    # Relationship: One-to-many with Lesson (Instructor)
    lessons = db.relationship('Lesson', back_populates='instructor', foreign_keys='Lesson.instructor_id', lazy=True)

    # Relationship: Many-to-many with Lesson (Student)
    student_lessons = db.relationship('Lesson', secondary=student_lessons, back_populates='students', lazy='dynamic')

    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

    def is_student(self):
        return self.role == 'STUDENT'

    def is_instructor(self):
        return self.role == 'INSTRUCTOR'

    def is_admin(self):
        return self.role == 'ADMIN'

# Assignment model
class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    grade = db.Column(db.Float, nullable=True)
    
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    instructor = db.relationship('User', back_populates='assignments', 
                               foreign_keys=[instructor_id])
    student = db.relationship('User', back_populates='student_assignments', 
                            foreign_keys=[student_id])

    submission = db.Column(db.Text, nullable=True)
    submitted_on = db.Column(db.DateTime, nullable=True)
    graded_on = db.Column(db.DateTime, nullable=True)

    def __init__(self, title, description, due_date, instructor_id):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.instructor_id = instructor_id
        self.status = 'pending'

    def submit(self, student_id, submission):
        self.student_id = student_id
        self.submission = submission
        self.submitted_on = datetime.utcnow()
        self.status = 'submitted'

    def grade_assignment(self, grade):
        self.grade = grade
        self.graded_on = datetime.utcnow()
        self.status = 'graded'

    def __repr__(self):
        return f'<Assignment {self.title}>'

# Lesson Model
class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)

    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    instructor = db.relationship('User', back_populates='lessons', foreign_keys=[instructor_id])
    students = db.relationship('User', secondary=student_lessons, back_populates='student_lessons', lazy='dynamic')

    def __init__(self, title, content, description, due_date, instructor_id):
        self.title = title
        self.content = content
        self.description = description
        self.due_date = due_date
        self.instructor_id = instructor_id

    def add_student(self, student):
        if not self.students.filter_by(id=student.id).first():
            self.students.append(student)

    def remove_student(self, student):
        if self.students.filter_by(id=student.id).first():
            self.students.remove(student)

    def __repr__(self):
        return f'<Lesson {self.title}>'