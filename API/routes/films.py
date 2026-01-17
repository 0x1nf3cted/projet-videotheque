from flask import Blueprint, request, jsonify
from utils.json_handler import lire_json, ecrire_json
import uuid
import os

films_bp = Blueprint('films', __name__)

@films_bp.route('/api/films', methods=['GET'])
def get_films():
    films = lire_json('films.json')
    
    genre_filter = request.args.get('genre', '').lower()
    annee_min = request.args.get('annee_min')
    annee_max = request.args.get('annee_max')
    note_min = request.args.get('note_min')
    format_filter = request.args.get('format', '').lower()
    sort_by = request.args.get('sort', 'titre')
    order = request.args.get('order', 'asc')
    
    if genre_filter:
        films = [f for f in films if genre_filter in f.get('genre', '').lower()]
    
    if annee_min:
        try:
            annee_min_int = int(annee_min)
            films = [f for f in films if f.get('annee', 0) >= annee_min_int]
        except ValueError:
            pass
    
    if annee_max:
        try:
            annee_max_int = int(annee_max)
            films = [f for f in films if f.get('annee', 9999) <= annee_max_int]
        except ValueError:
            pass
    
    if note_min:
        try:
            note_min_float = float(note_min)
            films = [f for f in films if f.get('note', 0) >= note_min_float]
        except ValueError:
            pass
    
    if format_filter:
        films = [f for f in films if format_filter in f.get('format', '').lower()]
    
    reverse_order = (order == 'desc')
    
    if sort_by == 'note':
        films.sort(key=lambda x: x.get('note', 0), reverse=reverse_order)
    elif sort_by == 'annee':
        films.sort(key=lambda x: x.get('annee', 0), reverse=reverse_order)
    elif sort_by == 'duree':
        films.sort(key=lambda x: x.get('duree', 0), reverse=reverse_order)
    elif sort_by == 'titre':
        films.sort(key=lambda x: x.get('titre', '').lower(), reverse=reverse_order)
    elif sort_by == 'realisateur':
        films.sort(key=lambda x: x.get('realisateur', '').lower(), reverse=reverse_order)
    elif sort_by == 'date_ajout':
        films.sort(key=lambda x: x.get('date_ajout', ''), reverse=reverse_order)
    
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
    

    film_to_delete = None
    for film in films:
        if film.get('id') == id:
            film_to_delete = film
            break
    
    if film_to_delete is None:
        return jsonify({'success': False, 'error': 'Film non trouvé', 'code': 404}), 404
    

    image_filename = film_to_delete.get('image')
    if image_filename:
        images_dir = os.environ.get('IMAGES_DIR', '/app/images')
        image_path = os.path.join(images_dir, image_filename)
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                print(f'Erreur lors de la suppression de l\'image: {e}')
    

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

@films_bp.route('/api/films/<film_id>/recommendations', methods=['GET'])
def get_recommendations(film_id):
    limit = int(request.args.get('limit', 10))
    
    films = lire_json('films.json')
    film = next((f for f in films if f.get('id') == film_id), None)
    
    if not film:
        return jsonify({'success': False, 'error': 'Film non trouvé', 'code': 404}), 404
    
    genre = film.get('genre', '')
    acteurs = film.get('acteurs', [])
    
    if not isinstance(acteurs, list):
        acteurs = []
    
    recommendations = []
    for f in films:
        if f.get('id') == film_id:
            continue
        
        score = 0
        
        if f.get('genre') == genre:
            score += 5
        
        acteurs_film = f.get('acteurs', [])
        if not isinstance(acteurs_film, list):
            acteurs_film = []
        
        acteurs_communs = set(acteurs) & set(acteurs_film)
        score += len(acteurs_communs) * 3
        
        if score > 0:
            f_copy = f.copy()
            f_copy['match_score'] = score
            recommendations.append(f_copy)
    
    recommendations.sort(key=lambda x: x['match_score'], reverse=True)
    
    return jsonify({
        'success': True,
        'data': recommendations[:limit],
        'total': len(recommendations)
    })

