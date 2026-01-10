# j'ai créer un seeder pour remplir la base de données avec les films de l'api TMDB
# la particularité de ce seeder et qu'il va relier les films avec les acteurs via leur id
# ce qui va nous permettre d'avoir plus de fonctionalité ou on croise les données

import os
import requests
import uuid
import random
from datetime import datetime
from utils.json_handler import lire_json, ecrire_json

TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
TMDB_BASE_URL = 'https://api.themoviedb.org/3' # pour les filsm
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w500' # pour les images, surtout les fims et acteurs

def recuperer_films_populaires(api_key, nombre=50):
    films = []
    acteurs_dict = {}
    page = 1
    
    # on récupère les films populaires page par page jusqu'à avoir assez
    while len(films) < nombre:
        url = f'{TMDB_BASE_URL}/movie/popular'
        params = {'api_key': api_key, 'page': page}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            for result in data.get('results', []):
                if len(films) >= nombre:
                    break
                    
                tmdb_id = result['id']
                film_detail, acteurs_film = obtenir_details_film(tmdb_id, api_key, acteurs_dict)
                if film_detail:
                    films.append(film_detail)
                    # on met à jour le dict avec les nouveaux acteurs
                    for acteur_info in acteurs_film:
                        tmdb_person_id = acteur_info.get('tmdb_id')
                        if tmdb_person_id:
                            if tmdb_person_id not in acteurs_dict:
                                acteurs_dict[tmdb_person_id] = acteur_info
                            # on ajoute le film dans la liste des films de l'acteur
                            if film_detail.get('id') not in acteurs_dict[tmdb_person_id].get('films', []):
                                acteurs_dict[tmdb_person_id]['films'].append(film_detail.get('id'))
            
            if not data.get('results') or len(data.get('results', [])) == 0:
                break
                
            page += 1
            
        except Exception as e:
            print(f'Erreur lors de la récupération: {e}')
            break
    

    acteurs_finaux = []
    for acteur in acteurs_dict.values():
        acteur_clean = {k: v for k, v in acteur.items() if k != 'tmdb_id'}
        acteurs_finaux.append(acteur_clean)
    
    return films[:nombre], acteurs_finaux

def obtenir_details_film(tmdb_id, api_key, acteurs_dict):
    try:
        url_detail = f'{TMDB_BASE_URL}/movie/{tmdb_id}'
        url_credits = f'{TMDB_BASE_URL}/movie/{tmdb_id}/credits'
        params = {'api_key': api_key}
        
        response_detail = requests.get(url_detail, params=params)
        response_detail.raise_for_status()
        detail = response_detail.json()
        
        response_credits = requests.get(url_credits, params=params)
        credits = {}
        if response_credits.status_code == 200:
            credits = response_credits.json()
        
        # on cherche le réalisateur dans la crew
        realisateur = None
        if 'crew' in credits:
            for person in credits['crew']:
                if person.get('job') == 'Director':
                    realisateur = person.get('name')
                    break
        
        genres = detail.get('genres', [])
        genre = genres[0].get('name', 'Inconnu') if genres else 'Inconnu'
        
        release_date = detail.get('release_date', '')
        annee = int(release_date[:4]) if release_date and len(release_date) >= 4 else None
        
        formats_possibles = ['numérique', 'DVD', 'Blu-ray']
        format_film = random.choice(formats_possibles)
        
        vote_avg = detail.get('vote_average', 0)
        note = round(vote_avg, 1) if vote_avg <= 10 else round(vote_avg / 10, 1)
        
        poster_path = detail.get('poster_path', '')
        image_url = None
        if poster_path:
            image_url = f'{TMDB_IMAGE_BASE}{poster_path}'
        
        # on crée l'id du film d'abord pour pouvoir l'utiliser dans les acteurs
        film_id = str(uuid.uuid4())
        
        # on récupère les acteurs de la liste des acteurs
        acteurs_ids = []
        acteurs_film = []
        cast = credits.get('cast', [])[:10]
        
        for cast_member in cast:
            person_id = cast_member.get('id')
            if person_id:
             
                if person_id in acteurs_dict:
                    acteurs_ids.append(acteurs_dict[person_id].get('id'))
                     
                    if film_id not in acteurs_dict[person_id].get('films', []):
                        acteurs_dict[person_id]['films'].append(film_id)
                else:
        
                    acteur_info = obtenir_details_acteur(person_id, api_key)
                    if acteur_info:
                        acteur_info['films'] = [film_id]
                        acteur_info['tmdb_id'] = person_id
                        acteurs_film.append(acteur_info)
                        acteurs_ids.append(acteur_info.get('id'))
        
        film = {
            'id': film_id,
            'titre': detail.get('title', ''),
            'realisateur': realisateur or 'Inconnu',
            'annee': annee,
            'genre': genre,
            'format': format_film,
            'duree': detail.get('runtime') or 0,
            'resume': detail.get('overview', '') or 'Aucun résumé disponible',
            'note': note,
            'acteurs': acteurs_ids,
            'image_url': image_url,
            'date_ajout': datetime.now().isoformat()
        }
        
        return film, acteurs_film
        
    except Exception as e:
        print(f'Erreur pour le film {tmdb_id}: {e}')
        return None, []

def obtenir_details_acteur(person_id, api_key):
    try:
        url = f'{TMDB_BASE_URL}/person/{person_id}'
        params = {'api_key': api_key}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        person = response.json()
        
        
        nom_complet = person.get('name', '')
        nom_parts = nom_complet.split(' ', 1)
        prenom = nom_parts[0] if len(nom_parts) > 0 else ''
        nom = nom_parts[1] if len(nom_parts) > 1 else prenom
        
 
        date_naissance = person.get('birthday', '')
        if date_naissance:
            try:
                datetime.strptime(date_naissance, '%Y-%m-%d')
            except:
                date_naissance = None
        
        # on récupère la nationalité (place_of_birth peut donner une indication)
        nationalite = person.get('place_of_birth', '')
        if nationalite:
            # on extrait juste le pays si c'est "Ville, Pays", pour apres mettre des emoji de pays
            if ',' in nationalite:
                nationalite = nationalite.split(',')[-1].strip()
        else:
            nationalite = 'Inconnue'
        
 
        profile_path = person.get('profile_path', '')
        image_url = None
        if profile_path:
            image_url = f'{TMDB_IMAGE_BASE}{profile_path}'
        
        acteur = {
            'id': str(uuid.uuid4()),
            'nom': nom,
            'prenom': prenom,
            'nationalite': nationalite,
            'date_naissance': date_naissance,
            'image_url': image_url,
            'films': []
        }
        
        return acteur
        
    except Exception as e:
        print(f'Erreur pour l\'acteur {person_id}: {e}')
        return None

def seed():
    if not TMDB_API_KEY:
        print('TMDB_API_KEY non définie, seeder ignoré')
        return
    
    films_existants = lire_json('films.json')
    if films_existants and len(films_existants) > 0:
        print(f'films.json contient déjà {len(films_existants)} films, seeder ignoré')
        return
    
    print('Début du seeder: récupération de 50 films depuis TMDb...')
    films, acteurs_list = recuperer_films_populaires(TMDB_API_KEY, 50)
    
    if films:
        # les acteurs sont déjà dédupliqués dans recuperer_films_populaires
        # on peut les sauvegarder directement
        ecrire_json('films.json', films)
        ecrire_json('acteurs.json', acteurs_list)
        print(f'Seeder terminé: {len(films)} films et {len(acteurs_list)} acteurs ajoutés')
    else:
        print('Aucun film récupéré')

if __name__ == '__main__':
    seed()

