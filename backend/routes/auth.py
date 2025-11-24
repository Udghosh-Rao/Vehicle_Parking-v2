from flask import request, jsonify, Blueprint
from flask_restful import Resource, Api
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from extensions import db
from models import VehicleUser

class Register(Resource):
    def post(self):
        data = request.get_json()
        
        if not all([data.get('Login_name'), data.get('Email_Address'), data.get('User_Password')]):
            return {'message': 'Missing required fields'}, 400
        
        if VehicleUser.query.filter_by(Email_Address=data.get('Email_Address')).first():
            return {'message': 'Email already registered'}, 400
        
        try:
            user = VehicleUser(
                Login_name=data.get('Login_name'),
                Full_Name=data.get('Full_Name'),
                Email_Address=data.get('Email_Address'),
                User_Password=generate_password_hash(data.get('User_Password')),
                Phone_Number=data.get('Phone_Number'),
                Pin_Code=data.get('Pin_Code'),
                Address=data.get('Address'),
                Role='user'
            )
            db.session.add(user)
            db.session.commit()
            return {'message': 'Registration successful'}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400


class AdminLogin(Resource):
    def post(self):
        data = request.get_json()
        user = VehicleUser.query.filter_by(Email_Address=data.get('Email_Address'), Role='admin').first()
        
        if not user or not check_password_hash(user.User_Password, data.get('User_Password')):
            return {'message': 'Invalid credentials'}, 401
        
        token = create_access_token(identity=user.User_id)
        return {
            'access_token': token,
            'user': {
                'User_id': user.User_id,
                'Full_Name': user.Full_Name,
                'Email_Address': user.Email_Address,
                'Role': user.Role
            }
        }, 200


class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        user = VehicleUser.query.filter_by(Email_Address=data.get('Email_Address')).first()
        
        if not user or not check_password_hash(user.User_Password, data.get('User_Password')):
            return {'message': 'Invalid credentials'}, 401
        
        token = create_access_token(identity=user.User_id)
        return {
            'access_token': token,
            'user': {
                'User_id': user.User_id,
                'Full_Name': user.Full_Name,
                'Email_Address': user.Email_Address,
                'Role': user.Role
            }
        }, 200


# Create blueprint and register resources
auth_bp = Blueprint('auth', __name__)
api = Api(auth_bp)

api.add_resource(Register, '/register')
api.add_resource(AdminLogin, '/admin-login')
api.add_resource(UserLogin, '/login')
