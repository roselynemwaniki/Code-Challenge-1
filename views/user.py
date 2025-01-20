from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User
from werkzeug.security import generate_password_hash

user_bp = Blueprint('user', __name__)

@user_bp.route('/current_user', methods=['GET'])
@jwt_required()
def current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({"username": user.username, "email": user.email}), 200

@user_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found!"}), 404
    data = request.get_json()
    if not data or ('username' not in data and 'email' not in data):
        return jsonify({"message": "Invalid data!"}), 400  # Return 400 if no valid data is provided
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify({"message": "User updated successfully!"}), 200

@user_bp.route('/updatepassword', methods=['PUT'])
@jwt_required()
def update_password():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found!"}), 404
    data = request.get_json()
    if 'new_password' in data:
        user.password = generate_password_hash(data['new_password'])  # Hash the new password
    db.session.commit()
    return jsonify({"message": "Password updated successfully!"}), 200

@user_bp.route('/delete_account', methods=['DELETE'])
@jwt_required()
def delete_account():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found!"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Account deleted successfully!"}), 200
