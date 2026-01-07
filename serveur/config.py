import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    API_URL = os.environ.get('API_URL', 'http://localhost:5001')
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
