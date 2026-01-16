from flask import Blueprint, request, jsonify
from utils.json_handler import lire_json, ecrire_json
import uuid
import os

films_bp = Blueprint('films', __name__)

@films_bp.route('/api/films', methods=['GET'])
def get_films():
    films = lire_json('films.json')
    return jsonify({'success': True, 'data': films})

@films_bp.route('/api/films/<id>', methods=['GET'])
def get_film(id):
    films = lire_json('films.json')
    film = next((f for f in films if f.get('id') == id), None)
    
    if film:
        return jsonify({'success': True, 'data': film})
    return jsonify({'success': False, 'error': 'Film non trouvé', 'code': 404}), 404

@films_bp.route('/api/films', methods=['POST'])
def create_film():
    data = request.get_json()
    
    if not data.get('titre'):
        return jsonify({'success': False, 'error': 'Le titre est requis', 'code': 400}), 400
    
    data['id'] = str(uuid.uuid4())
    
    films = lire_json('films.json')
    films.append(data)
    ecrire_json('films.json', films)
    
    return jsonify({'success': True, 'data': data}), 201

@films_bp.route('/api/films/<id>', methods=['PUT'])
def update_film(id):
    data = request.get_json()
    films = lire_json('films.json')
    
    film_index = None
    for i, film in enumerate(films):
        if film.get('id') == id:
            film_index = i
            break
    
    if film_index is None:
        return jsonify({'success': False, 'error': 'Film non trouvé', 'code': 404}), 404
    
    films[film_index] = {**films[film_index], **data, 'id': id}
    ecrire_json('films.json', films)
    
    return jsonify({'success': True, 'data': films[film_index]})

@films_bp.route('/api/films/<id>', methods=['DELETE'])
def delete_film(id):
    films = lire_json('films.json')
    
    # Trouver le film à supprimer pour récupérer l'image
    film_to_delete = None
    for film in films:
        if film.get('id') == id:
            film_to_delete = film
            break
    
    if film_to_delete is None:
        return jsonify({'success': False, 'error': 'Film non trouvé', 'code': 404}), 404
    
    # Supprimer l'image associée si elle existe
    image_filename = film_to_delete.get('image')
    if image_filename:
        images_dir = os.environ.get('IMAGES_DIR', '/app/images')
        image_path = os.path.join(images_dir, image_filename)
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                print(f'Erreur lors de la suppression de l\'image: {e}')
    
    # Supprimer le film de la liste
    films = [f for f in films if f.get('id') != id]
    ecrire_json('films.json', films)
    return jsonify({'success': True, 'message': 'Film supprimé'})

@films_bp.route('/api/films/search', methods=['GET'])
def search_films():
    query = request.args.get('q', '').lower()
    films = lire_json('films.json')
    
    if not query:
        return jsonify({'success': True, 'data': films})
    
    resultats = []
    for film in films:
        titre = film.get('titre', '').lower()
        realisateur = film.get('realisateur', '').lower()
        genre = film.get('genre', '').lower()
        
        if query in titre or query in realisateur or query in genre:
            resultats.append(film)
    
    return jsonify({'success': True, 'data': resultats})

