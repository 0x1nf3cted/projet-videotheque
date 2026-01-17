from flask import Blueprint, request, jsonify
from utils.json_handler import lire_json, ecrire_json
from datetime import datetime
import uuid

commentaires_bp = Blueprint('commentaires', __name__)

@commentaires_bp.route('/api/commentaires', methods=['POST'])
def ajouter_commentaire():
    data = request.get_json()
    film_id = data.get('film_id')
    user_id = data.get('user_id')
    note = data.get('note')
    commentaire = data.get('commentaire', '')
    
    if not film_id or not user_id:
        return jsonify({'success': False, 'error': 'film_id et user_id requis', 'code': 400}), 400
    
    if note is None or note < 0 or note > 10:
        return jsonify({'success': False, 'error': 'Note invalide (0-10)', 'code': 400}), 400
    
    films = lire_json('films.json')
    film = next((f for f in films if f.get('id') == film_id), None)
    
    if not film:
        return jsonify({'success': False, 'error': 'Film non trouvé', 'code': 404}), 404
    
    users = lire_json('users.json')
    user = next((u for u in users if u.get('id') == user_id), None)
    
    if not user:
        return jsonify({'success': False, 'error': 'Utilisateur non trouvé', 'code': 404}), 404
    
    commentaires = lire_json('commentaires.json')
    
    nouveau_commentaire = {
        'id': str(uuid.uuid4()),
        'film_id': film_id,
        'user_id': user_id,
        'username': user.get('username', ''),
        'note': float(note),
        'commentaire': commentaire,
        'date': datetime.now().isoformat()
    }
    
    commentaires.append(nouveau_commentaire)
    ecrire_json('commentaires.json', commentaires)
    
    return jsonify({'success': True, 'data': nouveau_commentaire}), 201

@commentaires_bp.route('/api/commentaires/film/<film_id>', methods=['GET'])
def commentaires_film(film_id):
    commentaires = lire_json('commentaires.json')
    commentaires_film = [c for c in commentaires if c.get('film_id') == film_id]
    
    commentaires_film.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    return jsonify({'success': True, 'data': commentaires_film})

@commentaires_bp.route('/api/commentaires/<commentaire_id>', methods=['DELETE'])
def supprimer_commentaire(commentaire_id):
    commentaires = lire_json('commentaires.json')
    commentaires = [c for c in commentaires if c.get('id') != commentaire_id]
    
    ecrire_json('commentaires.json', commentaires)
    return jsonify({'success': True, 'message': 'Commentaire supprimé'})

