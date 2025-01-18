from flask import Flask, jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import  JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import timedelta
from extensions import db


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


#User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)


# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))
        return jsonify(access_token=access_token), 200
    return jsonify({'message': 'Invalid credentials'}), 401


#Get current user
@app.route('/user', methods=['GET'])
@jwt_required
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    return jsonify({'username': user.username}), 200


#Logout
@app.route('/logout', methods=['POST'])
@jwt_required
def logout():
    return jsonify({'message': 'Logged out successfully'}), 200


#Update User Profile
@app.route('/update', methods=['PUT'])
@jwt_required
def update_user():
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    user.username = data['username']
    db.session.commit()
    return jsonify({'message': 'User updated successfully'}), 200


#Update User Password
@app.route('/update_password', methods=['PUT'])
@jwt_required
def update_password():
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    db.session.commit()
    return jsonify({'message': 'Password updated successfully'}), 200

#Delete User 
@app.route('/delete', methods=['DELETE'])
@jwt_required
def delete_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

#===========================Task===============================================

#Create Task
@app.route('/create_task', methods=['POST'])
@jwt_required
def create_task():
    data = request.get_json()
    task = Task(title=data['title'], description=data['description'], user_id=get_jwt_identity())
    db.session.add(task)
    db.session.commit()
    return jsonify({'message': 'Task created successfully'}), 200


#Read All Tasks
@app.route('/tasks', methods=['GET'])
@jwt_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=get_jwt_identity()).all()
    return jsonify([{'id': task.id, 'title': task.title, 'description': task
                     .description} for task in tasks]), 200 
#Read Task
@app.route('/task/<int:task_id>', methods=['GET'])
@jwt_required
def get_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=get_jwt_identity()).first()
    if task:
        return jsonify({'id': task.id, 'title': task.title, 'description': task.description
                        }), 200
    return jsonify({'message': 'Task not found'}), 404
#Update Task
@app.route('/update_task/<int:task_id>', methods=['PUT'])
@jwt_required
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=get_jwt_identity()).first()
    if task:
        data = request.get_json()
        task.title = data['title']
        task.description = data['description']
        db.session.commit()
        return jsonify({'message': 'Task updated successfully'}), 200
    return jsonify({'message': 'Task not found'}), 404

#Delete Task
@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
@jwt_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=get_jwt_identity()).first()
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully'}), 200
    return jsonify({'message': 'Task not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)  # Run the application in debug mode


