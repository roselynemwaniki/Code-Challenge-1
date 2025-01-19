import os  

class Config:  
    # Database configuration  
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')  # Use environment variable or SQLite  
    SQLALCHEMY_TRACK_MODIFICATIONS = False  
    
    # JWT configuration  
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your_jwt_secret_key')  # Change this in production  
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour  
    JWT_REFRESH_TOKEN_EXPIRES = 86400  # 1 day  
    JWT_BLACKLIST_ENABLED = True  
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']  
    JWT_HEADER_TYPE = 'Bearer'  
    JWT_HEADER_NAME = 'Authorization'