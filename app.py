from flask import Flask, jsonify, request  
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity  
from Models import db, User, Task  # Ensure this matches your directory structure  
from config import Config  
from flask_migrate import Migrate  
from werkzeug.security import generate_password_hash, check_password_hash  

app = Flask(__name__)  

# Load configuration from Config class  
app.config.from_object(Config)  

# Initialize extensions  
db.init_app(app)  
jwt = JWTManager(app)  
migrate = Migrate(app, db)  

@app.route('/register', methods=['POST'])  
def register():  
    data = request.get_json()  
    # Hash the password before storing it  
    hashed_password = generate_password_hash(data['password'], method='sha256')  
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)  
    db.session.add(new_user)  
    db.session.commit()  
    return jsonify({"message": "User registered successfully!"}), 201  

@app.route('/login', methods=['POST'])  
def login():  
    data = request.get_json()  
    user = User.query.filter_by(email=data['email']).first()  
    if user and check_password_hash(user.password, data['password']):  # Check hashed password  
        access_token = create_access_token(identity=user.id)  
        return jsonify(access_token=access_token), 200  
    return jsonify({"message": "Invalid credentials!"}), 401  

@app.route('/logout/', methods=['POST'])  
@jwt_required()  
def logout():  
    # Optional: add logic for blacklisting the token if needed  
    return jsonify({"message": "User logged out successfully!"}), 200  

@app.route('/current_user', methods=['GET'])  
@jwt_required()  
def current_user_without_auth_url(user_id):  
    # current_user_id = get_jwt_identity()  
    user = User.query.get(user_id)  
    if not user:  
        return jsonify({"message": "User not found!"}), 404  
    return jsonify({"username": user.username, "email": user.email}), 200  

@app.route('/user/update', methods=['PUT'])  
@jwt_required()  
def update_user():  
    current_user_id = get_jwt_identity()  
    user = User.query.get(current_user_id)  
    data = request.get_json()  
    user.username = data.get('username', user.username)  
    user.email = data.get('email', user.email)  
    db.session.commit()  
    return jsonify({"message": "User updated successfully!"}), 200  

@app.route('/user/updatepassword', methods=['PUT'])  
@jwt_required()  
def update_password():  
    current_user_id = get_jwt_identity()  
    user = User.query.get(current_user_id)  
    data = request.get_json()  
    # Hash the new password before storing it  
    user.password = generate_password_hash(data['new_password'], method='sha256')  
    db.session.commit()  
    return jsonify({"message": "Password updated successfully!"}), 200  

@app.route('/user/delete_account', methods=['DELETE'])  
@jwt_required()  
def delete_account():  
    current_user_id = get_jwt_identity()  
    user = User.query.get(current_user_id)  
    db.session.delete(user)  
    db.session.commit()  
    return jsonify({"message": "Account deleted successfully!"}), 200  

# CRUD for Task model  
@app.route('/task', methods=['POST'])  
@jwt_required()  
def create_task():  
    data = request.get_json()  
    new_task = Task(title=data['title'], description=data.get('description'), completed=data.get('completed', False))  
    db.session.add(new_task)  
    db.session.commit()  
    return jsonify({"message": "Task created successfully!"}), 201  

@app.route('/task', methods=['GET'])  
@jwt_required()  
def get_tasks():  
    tasks = Task.query.all()  
    return jsonify([{"id": task.id, "title": task.title, "description": task.description, "completed": task.completed} for task in tasks]), 200  

@app.route('/task/<int:task_id>', methods=['PUT'])  
@jwt_required()  
def update_task(task_id):  
    task = Task.query.get_or_404(task_id)  
    data = request.get_json()  
    task.title = data.get('title', task.title)  
    task.description = data.get('description', task.description)  
    task.completed = data.get('completed', task.completed)  
    db.session.commit()  
    return jsonify({"message": "Task updated successfully!"}), 200  

@app.route('/task/<int:task_id>', methods=['DELETE'])  
@jwt_required()  
def delete_task(task_id):  
    task = Task.query.get_or_404(task_id)  
    db.session.delete(task)  
    db.session.commit()  
    return jsonify({"message": "Task deleted successfully!"}), 200  

if __name__ == '__main__':  
    app.run(debug=True)