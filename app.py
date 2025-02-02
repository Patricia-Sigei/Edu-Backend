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
    CORS(app, supports_credentials=True, origins="*", allow_headers=["Content-Type", "Authorization"]) 
# using CORS to handle the JWT error
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

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

    # Debug route - properly indented inside create_app
    @app.route('/api/debug/token', methods=['GET'])
    def debug_token():
        auth_header = request.headers.get('Authorization')
        all_headers = dict(request.headers)
        return jsonify({
            'status': 'debug',
            'auth_header': auth_header,
            'all_headers': all_headers,
            'env_secret': app.config['JWT_SECRET_KEY']
        })

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

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)