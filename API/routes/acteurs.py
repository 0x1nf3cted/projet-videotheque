# fichier qui contient les routes pour les acteurs
# les fichiers sont stocké dans le volume docker

from flask import Blueprint, request, jsonify
from utils.json_handler import lire_json, ecrire_json
import uuid

acteurs_bp = Blueprint('acteurs', __name__)

@acteurs_bp.route('/api/acteurs', methods=['GET'])
def get_acteurs():
    acteurs = lire_json('acteurs.json')
    return jsonify({'success': True, 'data': acteurs})

@acteurs_bp.route('/api/acteurs/<id>', methods=['GET'])
def get_acteur(id):
    acteurs = lire_json('acteurs.json')
    acteur = next((a for a in acteurs if a.get('id') == id), None)
    
    if acteur:
        return jsonify({'success': True, 'data': acteur})
    return jsonify({'success': False, 'error': 'Acteur non trouvé', 'code': 404}), 404

@acteurs_bp.route('/api/acteurs', methods=['POST'])
def create_acteur():
    data = request.get_json()
    
    if not data.get('nom') or not data.get('prenom'):
        return jsonify({'success': False, 'error': 'Le nom et prénom sont requis', 'code': 400}), 400
    
    data['id'] = str(uuid.uuid4())
    if 'films' not in data:
        data['films'] = []
    
    acteurs = lire_json('acteurs.json')
    acteurs.append(data)
    ecrire_json('acteurs.json', acteurs)
    
    return jsonify({'success': True, 'data': data}), 201

