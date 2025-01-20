from flask import Flask, jsonify, request  
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity  
from flask_sqlalchemy import SQLAlchemy  
from werkzeug.security import generate_password_hash, check_password_hash  
from flask_migrate import Migrate  
from sqlalchemy.exc import IntegrityError 
from datetime import datetime
import re

# Import the User model
from models import db, User

# Initialize Flask app  
app = Flask(__name__)  

# Database and JWT configuration  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///App.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.config['JWT_SECRET_KEY'] = 'super-secret'    
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600    
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 3600   
app.config['JWT_BLACKLIST_ENABLED'] = True  
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']  
app.config['JWT_HEADER_TYPE'] = 'Bearer'  
app.config['JWT_HEADER_NAME'] = 'Authorization'  

# Initialize extensions  
db = SQLAlchemy()  
db.init_app(app)  
jwt = JWTManager(app)  
migrate = Migrate(app, db) 

# JWT error responses  
@jwt.unauthorized_loader  
def unauthorized_response(callback):  
    return jsonify({"msg": "Missing Authorization Header"}), 401  

@jwt.invalid_token_loader  
def invalid_token_response(callback):  
    return jsonify({"msg": "Invalid token"}), 401  

# Email validation function
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Root route
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the User Management API!"}), 200

# User registration endpoint  
@app.route('/register', methods=['POST'])  
def register():      
    data = request.get_json()  
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:  
        return jsonify({"message": "Missing required fields!"}), 400  

    if not is_valid_email(data['email']):
        return jsonify({"message": "Invalid email format!"}), 400

    hashed_password = generate_password_hash(data['password'])   
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)  # Corrected line

    try:  
        db.session.add(new_user)  
        db.session.commit()  
        return jsonify({"message": "User registered successfully!"}), 201  
    except IntegrityError:  
        db.session.rollback()  
        return jsonify({"message": "User already exists!"}), 400  
    except Exception as e:  
        return jsonify({"message": str(e)}), 500  

# User login endpoint  
@app.route('/login', methods=['POST'])  
@jwt_required()  
def login():  
    data = request.get_json()  
    user = User.query.filter_by(email=data['email']).first()  
    if user and check_password_hash(user.password, data['password']):  
        access_token = create_access_token(identity=user.id)  
        return jsonify(access_token=access_token), 200  
    return jsonify({"message": "Invalid credentials!"}), 401  

# User logout endpoint  
@app.route('/logout', methods=['POST'])  
@jwt_required()  
def logout():  
    return jsonify({"message": "Successfully logged out!"}), 200  

# Get current user information  
@app.route('/current_user', methods=['GET'])  
@jwt_required()  
def current_user():  
    current_user_id = get_jwt_identity()  
    user = db.session.get(User, current_user_id)  # Updated line
    return jsonify({"username": user.username, "email": user.email}), 200  

# Update user information  
@app.route('/user/update', methods=['PUT'])  
@jwt_required()  
def update_user():  
    current_user_id = get_jwt_identity()  
    user = db.session.get(User, current_user_id)  # Updated line
    data = request.get_json()  
    user.username = data.get('username', user.username)  
    user.email = data.get('email', user.email)  
    db.session.commit()  
    return jsonify({"message": "User updated successfully!"}), 200  

# Update user password  
@app.route('/user/updatepassword', methods=['PUT'])  
@jwt_required()  
def update_password():  
    current_user_id = get_jwt_identity()  
    user = db.session.get(User, current_user_id)  # Updated line
    data = request.get_json()  
    user.password = generate_password_hash(data['new_password'])   
    db.session.commit()  
    return jsonify({"message": "Password updated successfully!"}), 200

# Delete user account  
@app.route('/user/delete_account', methods=['DELETE'])  
@jwt_required()  
def delete_account():  
    current_user_id = get_jwt_identity()  
    user = db.session.get(User, current_user_id)  
    db.session.delete(user)  
    db.session.commit()  
    return jsonify({"message": "Account deleted successfully!"}), 200  

# CRUD for Task model  
@app.route('/task', methods=['POST'])  
@jwt_required()  
def create_task(Task):  
    data = request.get_json()  
    if not data or 'title' not in data or 'user_id' not in data:
        return jsonify({"message": "Missing required fields!"}), 400

    new_task = Task(  
        title=data['title'],   
        description=data.get('description'),   
        completed=data.get('completed', False),  
        user_id=get_jwt_identity()  # Associate task with the user
    )  
    db.session.add(new_task)  
    db.session.commit()  
    return jsonify({"message": "Task created successfully!"}), 201  

@app.route('/task', methods=['GET'])  
@jwt_required()  
def get_tasks(Task):  
    current_user_id = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=current_user_id).all()  # Get tasks for the current user
    return jsonify([{"id": task.id, "title": task.title, "description": task.description, "completed": task.completed} for task in tasks]), 200  

@app.route('/task/<int:task_id>', methods=['PUT'])  
@jwt_required()  
def update_task(task_id, Task):  
    task = Task.query.get_or_404(task_id)  
    data = request.get_json()  
    task.title = data.get('title', task.title)  
    task.description = data.get('description', task.description)  
    task.completed = data.get('completed', task.completed)  
    db.session.commit()  
    return jsonify({"message": "Task updated successfully!"}), 200  

@app.route('/task/<int:task_id>', methods=['DELETE'])  
@jwt_required()  
def delete_task(task_id, Task):  
    task = Task.query.get_or_404(task_id)  
    db.session.delete(task)  
    db.session.commit()  
    return jsonify({"message": "Task deleted successfully!"}), 200  

@app.errorhandler(404)
def not_found(error):
    return jsonify({"message": "The requested URL was not found on the server."}), 404

if __name__ == '__main__':  
    app.run(debug=True)
