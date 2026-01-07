import jwt
import datetime
from functools import wraps
from flask import request, jsonify
import os

SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
ALGORITHM = 'HS256'
TOKEN_EXPIRE_APRES = 24

def generer_token(user_id, username):
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRE_APRES),
        'iat': datetime.datetime.utcnow()
    }
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY n'est pas défini")
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verifier_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({
                    'success': False,
                    'error': 'Token invalide',
                    'code': 401
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token manquant',
                'code': 401
            }), 401
        
        payload = verifier_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'error': 'Token invalide ou expiré',
                'code': 401
            }), 401
        
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated
