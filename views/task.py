from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Task

task_bp = Blueprint('task', __name__)

def check_authorization():
    if not request.headers.get('Authorization'):
        return jsonify({"message": "Missing Authorization Header"}), 401

@task_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    check_authorization()
    data = request.get_json()
    if not data or 'title' not in data or 'user_id' not in data:
        return jsonify({"message": "Missing required fields!"}), 400

    new_task = Task(
        title=data['title'],
        description=data.get('description'),
        completed=data.get('completed', False),
        user_id=data['user_id']
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task created successfully!"}), 201

@task_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    check_authorization()
    tasks = Task.query.all()
    return jsonify([{
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed
    } for task in tasks]), 200

@task_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    check_authorization()
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Task not found!"}), 404
    data = request.get_json()
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)
    db.session.commit()
    return jsonify({"message": "Task updated successfully!"}), 200

@task_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    check_authorization()
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Task not found!"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted successfully!"}), 200
