from flask import Blueprint, request, jsonify
from utils.json_handler import lire_json, ecrire_json
from utils.auth import generer_token, verifier_token
import uuid
import hashlib
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')
    
    if not username or not password:
        return jsonify({
            'success': False,
            'error': 'Username et password requis',
            'code': 400
        }), 400
    
    users = lire_json('users.json')
    
    if any(u.get('username') == username or u.get('email') == email for u in users):
        return jsonify({
            'success': False,
            'error': 'Username ou email déjà utilisé',
            'code': 409
        }), 409
    
    new_user = {
        'id': str(uuid.uuid4()),
        'username': username,
        'password': hash_password(password),
        'email': email,
        'date_creation': datetime.now().isoformat()
    }
    
    users.append(new_user)
    ecrire_json('users.json', users)
    
    token = generer_token(new_user['id'], username)
    
    return jsonify({
        'success': True,
        'message': 'Utilisateur créé avec succès',
        'data': {
            'user_id': new_user['id'],
            'username': username,
            'token': token
        }
    }), 201

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({
            'success': False,
            'error': 'Username et password requis',
            'code': 400
        }), 400
    
    users = lire_json('users.json')
    
    user = next((u for u in users if u.get('username') == username), None)
    

    hashed_password = hash_password(password)
    if not user or user.get('password') != hashed_password:
        return jsonify({
            'success': False,
            'error': 'Identifiants invalides',
            'code': 401
        }), 401
    
    token = generer_token(user['id'], username)
    
    return jsonify({
        'success': True,
        'message': 'Connexion réussie',
        'data': {
            'user_id': user['id'],
            'username': username,
            'email': user.get('email', ''),
            'token': token
        }
    }), 200

@auth_bp.route('/api/auth/verify', methods=['POST'])
def verify():
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({
            'success': False,
            'error': 'Token manquant',
            'code': 400
        }), 400
    
    payload = verifier_token(token)
    if payload:
        return jsonify({
            'success': True,
            'data': {
                'user_id': payload.get('user_id'),
                'username': payload.get('username')
            }
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': 'Token invalide ou expiré',
            'code': 401
        }), 401
