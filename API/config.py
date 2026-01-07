import os

class Config:
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24
    PORT = int(os.environ.get('PORT', 5001))
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
