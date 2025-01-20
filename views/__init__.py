from flask import Flask
from .auth import auth_bp  
from .user import user_bp  
from .task import task_bp  

def create_views(app: Flask):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(task_bp, url_prefix='/task')
