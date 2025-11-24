from flask import Flask, jsonify
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

from config import config
from extensions import db, migrate, jwt, cache, init_extensions
from models import VehicleUser

def create_app(config_name='development'):
    """Create Flask app"""
    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    # Initialize extensions
    init_extensions(app)

    # JWT handlers
    @jwt.unauthorized_loader
    def unauthorized(msg):
        return jsonify({"message": "Missing or invalid token"}), 401

    @jwt.invalid_token_loader
    def invalid_token(msg):
        return jsonify({"message": "Invalid token"}), 401

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_data):
        return jsonify({"message": "Token expired"}), 401

    # === FIXED: Use relative import so Celery/Flask both work ===
    from routes import register_routes

    register_routes(app)

    # Create database and admin
    with app.app_context():
        db.create_all()

        admin = VehicleUser.query.filter_by(Email_Address='udghosh@gmail.com').first()
        if not admin:
            admin = VehicleUser(
                Login_name='Udghosh Admin',
                Full_Name='Udghosh Admin Vehicle Parking',
                Email_Address='udghosh@gmail.com',
                User_Password=generate_password_hash('1234'),
                Phone_Number='9799838874',
                Role='admin',
                Address='Delhi',
                Pin_Code='1100333'
            )
            db.session.add(admin)
            db.session.commit()
            print("[DB] Admin = udghosh@gmail.com / 1234")

        print("[DB] ✓ Database initialized")

    # Health check
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({"status": "online"}), 200

    # Root
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            "app": "Vehicle Parking App",
            "version": "2.0",
            "status": "running"
        }), 200

    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)
