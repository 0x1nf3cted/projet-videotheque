from flask import Blueprint, request, jsonify
from utils.json_handler import lire_json, ecrire_json

favoris_bp = Blueprint('favoris', __name__)

@favoris_bp.route('/api/favoris', methods=['POST'])
def ajouter_favori():
    data = request.get_json()
    film_id = data.get('film_id')
    user_id = data.get('user_id')
    
    if not film_id or not user_id:
        return jsonify({'success': False, 'error': 'film_id et user_id requis', 'code': 400}), 400
    
    films = lire_json('films.json')
    film = next((f for f in films if f.get('id') == film_id), None)
    
    if not film:
        return jsonify({'success': False, 'error': 'Film non trouvé', 'code': 404}), 404
    
    favoris = lire_json('favoris.json')
    deja_favori = next((f for f in favoris if f.get('user_id') == user_id and f.get('film_id') == film_id), None)
    
    if deja_favori:
        return jsonify({'success': False, 'error': 'Film déjà en favoris', 'code': 409}), 409
    
    favoris.append({
        'user_id': user_id,
        'film_id': film_id
    })
    
    ecrire_json('favoris.json', favoris)
    return jsonify({'success': True, 'message': 'Film ajouté aux favoris'}), 201

@favoris_bp.route('/api/favoris/<user_id>', methods=['GET'])
def mes_favoris(user_id):
    favoris = lire_json('favoris.json')
    films_favoris_ids = [f.get('film_id') for f in favoris if f.get('user_id') == user_id]
    
    films = lire_json('films.json')
    films_favoris = [f for f in films if f.get('id') in films_favoris_ids]
    
    return jsonify({'success': True, 'data': films_favoris})

@favoris_bp.route('/api/favoris', methods=['DELETE'])
def supprimer_favori():
    data = request.get_json()
    film_id = data.get('film_id')
    user_id = data.get('user_id')
    
    if not film_id or not user_id:
        return jsonify({'success': False, 'error': 'film_id et user_id requis', 'code': 400}), 400
    
    favoris = lire_json('favoris.json')
    favoris = [f for f in favoris if not (f.get('user_id') == user_id and f.get('film_id') == film_id)]
    
    ecrire_json('favoris.json', favoris)
    return jsonify({'success': True, 'message': 'Film retiré des favoris'})

@favoris_bp.route('/api/favoris/check', methods=['POST'])
def verifier_favori():
    data = request.get_json()
    film_id = data.get('film_id')
    user_id = data.get('user_id')
    
    if not film_id or not user_id:
        return jsonify({'success': False, 'is_favorite': False}), 400
    
    favoris = lire_json('favoris.json')
    is_favorite = any(f.get('user_id') == user_id and f.get('film_id') == film_id for f in favoris)
    
    return jsonify({'success': True, 'is_favorite': is_favorite})

