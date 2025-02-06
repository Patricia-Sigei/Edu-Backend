from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from models import db  

# Initialize other extensions
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Configure CORS 
    CORS(app, supports_credentials=True, origins="*", allow_headers="*") 

    # JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'status': 'error',
            'message': 'Invalid token'
        }), 422

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({
            'status': 'error',
            'message': 'Missing Authorization Header'
        }), 401


    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.admin_routes import admin_bp
    from routes.instructor_routes import instructor_bp
    from routes.student_routes import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(instructor_bp)
    app.register_blueprint(student_bp)

    # Create tables and admin user within app context
    with app.app_context():
        from models import User
        from werkzeug.security import generate_password_hash
        
        # Create all tables
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username="ADM-001").first()
        if not admin:
            admin = User(
                username="ADM-001", 
                password=generate_password_hash("Admin@123"), 
                role="ADMIN"
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")

      # manually create instructor for testing
        instructor = User.query.filter_by(username="INST-001").first()
        if not instructor:
            instructor = User(
                username="INST-001", 
                password=generate_password_hash("Instructor@123"), 
                role="INSTRUCTOR"
            )
            db.session.add(instructor)
            db.session.commit()
            print("Instructor user created successfully!")

         # manually create student for testing
        instructor = User.query.filter_by(username="SFT-001").first()
        if not student:
            student = User(
                username="SFT-001", 
                password=generate_password_hash("Student@123"), 
                role="STUDENT"
            )
            db.session.add(student)
            db.session.commit()
            print("Student user created successfully!")

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
