from flask_sqlalchemy import SQLAlchemy  
from werkzeug.security import generate_password_hash, check_password_hash  

db = SQLAlchemy()  

# User model  
class User(db.Model):  
    __tablename__ = 'users'  # table name in the database  

    id = db.Column(db.Integer, primary_key=True)  
    username = db.Column(db.String(80), nullable=False, unique=True)  
    email = db.Column(db.String(120), nullable=False, unique=True)  
    password = db.Column(db.String(256), nullable=False)  

    # Relationship with Task model  
    tasks = db.relationship('Task', backref='owner', lazy=True)  

    def __repr__(self):  
        return f'<User {self.username}>'  

    def set_password(self, password):  
        self.password = generate_password_hash(password)  

    def check_password(self, password):  
        return check_password_hash(self.password, password)  


# Task model  
class Task(db.Model):  
    __tablename__ = 'tasks'  # table name in the database  

    id = db.Column(db.Integer, primary_key=True)  
    title = db.Column(db.String(150), nullable=False)  
    description = db.Column(db.String(500), nullable=True)  
    completed = db.Column(db.Boolean, default=False)  

    # Foreign key to the User model  
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  

    def __repr__(self):  
        return f'<Task {self.title}>'