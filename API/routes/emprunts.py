# fichier pour gerer les emprunts des films

from flask import Blueprint, request, jsonify
from utils.json_handler import lire_json, ecrire_json
from datetime import datetime, timedelta

emprunts_bp = Blueprint('emprunts', __name__)

@emprunts_bp.route('/api/emprunts', methods=['POST'])
def emprunter_film():
    data = request.get_json()
    film_id = data.get('film_id')
    user_id = data.get('user_id')
    
    if not film_id or not user_id:
        return jsonify({'success': False, 'error': 'film_id et user_id requis', 'code': 400}), 400
    
    films = lire_json('films.json')
    film = next((f for f in films if f.get('id') == film_id), None)
    
    if not film:
        return jsonify({'success': False, 'error': 'Film non trouvé', 'code': 404}), 404
    
    if film.get('emprunt') and film['emprunt'].get('user_id'):
        return jsonify({'success': False, 'error': 'Film déjà emprunté', 'code': 409}), 409
    
    date_emprunt = datetime.now().isoformat()
    date_retour = (datetime.now() + timedelta(days=7)).isoformat()
    
    # stockage de donnees liés a l'emprunt de film, pour la tracabilité
    film['emprunt'] = {
        'user_id': user_id,
        'date_emprunt': date_emprunt,
        'date_retour': date_retour
    }
    
    for i, f in enumerate(films):
        if f.get('id') == film_id:
            films[i] = film
            break
    
    ecrire_json('films.json', films)
    return jsonify({'success': True, 'data': film}), 201

@emprunts_bp.route('/api/emprunts/<user_id>', methods=['GET'])
def mes_emprunts(user_id):
    films = lire_json('films.json')
    emprunts = [f for f in films if f.get('emprunt') and f['emprunt'].get('user_id') == user_id]
    return jsonify({'success': True, 'data': emprunts})

@emprunts_bp.route('/api/emprunts/<film_id>', methods=['DELETE'])
def retourner_film(film_id):
    films = lire_json('films.json')
    film = next((f for f in films if f.get('id') == film_id), None)
    
    if not film:
        return jsonify({'success': False, 'error': 'Film non trouvé', 'code': 404}), 404
    
    if not film.get('emprunt'):
        return jsonify({'success': False, 'error': 'Film non emprunté', 'code': 400}), 400
    
    film['emprunt'] = None
    
    for i, f in enumerate(films):
        if f.get('id') == film_id:
            films[i] = film
            break
    
    ecrire_json('films.json', films)
    return jsonify({'success': True, 'message': 'Film retourné'})

