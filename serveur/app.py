from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
API_URL = os.environ.get('API_URL', 'http://localhost:5001')
API_PUBLIC_URL = os.environ.get('API_PUBLIC_URL', 'http://localhost:5001')   
IMAGES_DIR = os.environ.get('IMAGES_DIR', '/app/images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024   

 
os.makedirs(IMAGES_DIR, exist_ok=True)

def is_authenticated():
    return 'token' in session and session.get('token')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_api_url():
    return dict(api_url=API_PUBLIC_URL)

@app.route('/')
def index():
    if not is_authenticated():
        return redirect(url_for('login'))
    
    try:
        response = requests.get(f'{API_URL}/api/films')
        films = []
        if response.status_code == 200:
            data = response.json()
            films = data.get('data', [])[:5]
        return render_template('index.html', username=session.get('username'), films=films)
    except Exception as e:
        return render_template('index.html', username=session.get('username'), films=[])

@app.route('/films')
def liste_films():
    if not is_authenticated():
        return redirect(url_for('login'))
    
    try:
        response = requests.get(f'{API_URL}/api/films')
        if response.status_code == 200:
            data = response.json()
            films = data.get('data', [])
            return render_template('films/liste.html', films=films)
        else:
            flash('Erreur lors de la récupération des films', 'error')
            return render_template('films/liste.html', films=[])
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
        return render_template('films/liste.html', films=[])

@app.route('/films/<id>')
def details_film(id):
    if not is_authenticated():
        return redirect(url_for('login'))
    
    try:
        response = requests.get(f'{API_URL}/api/films/{id}')
        if response.status_code == 200:
            data = response.json()
            film = data.get('data', {})
            
            acteurs = []
            acteurs_ids = film.get('acteurs', [])
            if acteurs_ids:
                response_acteurs = requests.get(f'{API_URL}/api/acteurs')
                if response_acteurs.status_code == 200:
                    acteurs_data = response_acteurs.json()
                    tous_acteurs = acteurs_data.get('data', [])
                    acteurs = [a for a in tous_acteurs if a.get('id') in acteurs_ids]
            
            user_id = session.get('user_id')
            is_favorite = False
            if user_id:
                check_response = requests.post(f'{API_URL}/api/favoris/check', json={'film_id': id, 'user_id': user_id})
                if check_response.status_code == 200:
                    check_data = check_response.json()
                    is_favorite = check_data.get('is_favorite', False)
            
            commentaires = []
            comments_response = requests.get(f'{API_URL}/api/commentaires/film/{id}')
            if comments_response.status_code == 200:
                comments_data = comments_response.json()
                commentaires = comments_data.get('data', [])
            
            return render_template('films/details.html', film=film, acteurs=acteurs, is_favorite=is_favorite, commentaires=commentaires)
        else:
            flash('Film non trouvé', 'error')
            return redirect(url_for('liste_films'))
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
        return redirect(url_for('liste_films'))

@app.route('/films/ajouter', methods=['GET', 'POST'])
def ajouter_film():
    if not is_authenticated():
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
 
            image_filename = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    # on verifie la taille de fichier d'image, la taille max est 5mb
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    
                    if file_size > MAX_FILE_SIZE:
                        flash('Le fichier image est trop volumineux (max 5MB)', 'error')
                        return render_template('films/ajouter.html')
                    
 
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    image_filename = f"{uuid.uuid4()}.{ext}"
                    file_path = os.path.join(IMAGES_DIR, image_filename)
                    file.save(file_path)
            
            data = {
                'titre': request.form.get('titre'),
                'realisateur': request.form.get('realisateur', ''),
                'annee': int(request.form.get('annee')) if request.form.get('annee') else None,
                'genre': request.form.get('genre', ''),
                'format': request.form.get('format', 'numérique'),
                'duree': int(request.form.get('duree')) if request.form.get('duree') else 0,
                'resume': request.form.get('resume', ''),
                'note': float(request.form.get('note')) if request.form.get('note') else 0.0,
                'acteurs': [],
                'date_ajout': None
            }
            
 
            if image_filename:
                data['image'] = image_filename
            
            response = requests.post(f'{API_URL}/api/films', json=data)
            if response.status_code == 201:
                flash('Film ajouté avec succès!', 'success')
                return redirect(url_for('liste_films'))
            else:
                error_data = response.json()
                flash(error_data.get('error', 'Erreur lors de l\'ajout'), 'error')
        except Exception as e:
            flash(f'Erreur: {str(e)}', 'error')
    
    return render_template('films/ajouter.html')

@app.route('/films/<id>/modifier', methods=['GET', 'POST'])
def modifier_film(id):
    if not is_authenticated():
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
 
            film_response = requests.get(f'{API_URL}/api/films/{id}')
            current_film = {}
            if film_response.status_code == 200:
                current_film = film_response.json().get('data', {})
            
 
            image_filename = current_film.get('image')   
            
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
 
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    
                    if file_size > MAX_FILE_SIZE:
                        flash('Le fichier image est trop volumineux (max 5MB)', 'error')
                        return redirect(url_for('modifier_film', id=id))
                    
 
                    old_image = current_film.get('image')
                    if old_image:
                        old_image_path = os.path.join(IMAGES_DIR, old_image)
                        if os.path.exists(old_image_path):
                            try:
                                os.remove(old_image_path)
                            except Exception as e:
                                print(f'Erreur lors de la suppression de l\'ancienne image: {e}')
                    
 
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    image_filename = f"{uuid.uuid4()}.{ext}"
                    file_path = os.path.join(IMAGES_DIR, image_filename)
                    file.save(file_path)
            
            data = {
                'titre': request.form.get('titre'),
                'realisateur': request.form.get('realisateur', ''),
                'annee': int(request.form.get('annee')) if request.form.get('annee') else None,
                'genre': request.form.get('genre', ''),
                'format': request.form.get('format', 'numérique'),
                'duree': int(request.form.get('duree')) if request.form.get('duree') else 0,
                'resume': request.form.get('resume', ''),
                'note': float(request.form.get('note')) if request.form.get('note') else 0.0
            }
            
 
            if image_filename:
                data['image'] = image_filename
            
            response = requests.put(f'{API_URL}/api/films/{id}', json=data)
            if response.status_code == 200:
                flash('Film modifié avec succès!', 'success')
                return redirect(url_for('details_film', id=id))
            else:
                error_data = response.json()
                flash(error_data.get('error', 'Erreur lors de la modification'), 'error')
        except Exception as e:
            flash(f'Erreur: {str(e)}', 'error')
    
    try:
        response = requests.get(f'{API_URL}/api/films/{id}')
        if response.status_code == 200:
            data = response.json()
            film = data.get('data', {})
            return render_template('films/modifier.html', film=film)
        else:
            flash('Film non trouvé', 'error')
            return redirect(url_for('liste_films'))
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
        return redirect(url_for('liste_films'))

@app.route('/films/<id>/supprimer', methods=['POST'])
def supprimer_film(id):
    if not is_authenticated():
        return redirect(url_for('login'))
    
    try:
        response = requests.delete(f'{API_URL}/api/films/{id}')
        if response.status_code == 200:
            flash('Film supprimé avec succès!', 'success')
        else:
            error_data = response.json()
            flash(error_data.get('error', 'Erreur lors de la suppression'), 'error')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('liste_films'))

@app.route('/films/recherche', methods=['GET', 'POST'])
def recherche_films():
    if not is_authenticated():
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        query = request.form.get('q', '')
        return redirect(url_for('resultats_recherche', q=query))
    
    return render_template('films/recherche.html')

@app.route('/films/resultats')
def resultats_recherche():
    if not is_authenticated():
        return redirect(url_for('login'))
    
    query = request.args.get('q', '')
    
    if not query:
        return redirect(url_for('recherche_films'))
    
    try:
        response = requests.get(f'{API_URL}/api/films/search', params={'q': query})
        if response.status_code == 200:
            data = response.json()
            films = data.get('data', [])
            return render_template('films/resultats.html', films=films, query=query)
        else:
            flash('Erreur lors de la recherche', 'error')
            return render_template('films/resultats.html', films=[], query=query)
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
        return render_template('films/resultats.html', films=[], query=query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Veuillez remplir tous les champs', 'error')
            return render_template('auth/login.html')
        
        try:
            response = requests.post(
                f'{API_URL}/api/auth/login',
                json={'username': username, 'password': password}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    session['token'] = data['data']['token']
                    session['username'] = data['data']['username']
                    session['user_id'] = data['data']['user_id']
                    flash('Connexion réussie!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash(data.get('error', 'Erreur de connexion'), 'error')
            else:
                error_data = response.json()
                flash(error_data.get('error', 'Identifiants invalides'), 'error')
        except Exception as e:
            flash(f'Erreur de connexion: {str(e)}', 'error')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email', '')
        
        if not username or not password:
            flash('Veuillez remplir tous les champs obligatoires', 'error')
            return render_template('auth/register.html')
        
        try:
            response = requests.post(
                f'{API_URL}/api/auth/register',
                json={'username': username, 'password': password, 'email': email}
            )
            
            if response.status_code == 201:
                data = response.json()
                if data.get('success'):
                    flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
                    return redirect(url_for('login'))
                else:
                    flash(data.get('error', 'Erreur lors de l\'inscription'), 'error')
            else:
                error_data = response.json()
                flash(error_data.get('error', 'Erreur lors de l\'inscription'), 'error')
        except Exception as e:
            flash(f'Erreur lors de l\'inscription: {str(e)}', 'error')
    
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('login'))

@app.route('/films/<id>/emprunter', methods=['POST'])
def emprunter_film(id):
    if not is_authenticated():
        return redirect(url_for('login'))
    
    try:
        user_id = session.get('user_id')
        response = requests.post(f'{API_URL}/api/emprunts', json={'film_id': id, 'user_id': user_id})
        if response.status_code == 201:
            flash('Film emprunté avec succès!', 'success')
        elif response.status_code == 409:
            flash('Ce film est déjà emprunté', 'error')
        else:
            error_data = response.json()
            flash(error_data.get('error', 'Erreur lors de l\'emprunt'), 'error')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('details_film', id=id))

@app.route('/mes-emprunts')
def mes_emprunts():
    if not is_authenticated():
        return redirect(url_for('login'))
    
    try:
        user_id = session.get('user_id')
        response = requests.get(f'{API_URL}/api/emprunts/{user_id}')
        if response.status_code == 200:
            data = response.json()
            films = data.get('data', [])
            return render_template('films/mes_emprunts.html', films=films)
        else:
            return render_template('films/mes_emprunts.html', films=[])
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
        return render_template('films/mes_emprunts.html', films=[])

@app.route('/films/<id>/retourner', methods=['POST'])
def retourner_film(id):
    if not is_authenticated():
        return redirect(url_for('login'))
    
    try:
        response = requests.delete(f'{API_URL}/api/emprunts/{id}')
        if response.status_code == 200:
            flash('Film retourné avec succès!', 'success')
        else:
            error_data = response.json()
            flash(error_data.get('error', 'Erreur lors du retour'), 'error')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('mes_emprunts'))

@app.route('/mes-favoris')
def mes_favoris():
    if not is_authenticated():
        return redirect(url_for('login'))
    
    try:
        user_id = session.get('user_id')
        response = requests.get(f'{API_URL}/api/favoris/{user_id}')
        if response.status_code == 200:
            data = response.json()
            films = data.get('data', [])
            return render_template('films/mes_favoris.html', films=films)
        else:
            return render_template('films/mes_favoris.html', films=[])
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
        return render_template('films/mes_favoris.html', films=[])

@app.route('/films/<id>/favoris', methods=['POST'])
def ajouter_favori(id):
    if not is_authenticated():
        return redirect(url_for('login'))
    
    try:
        user_id = session.get('user_id')
        response = requests.post(f'{API_URL}/api/favoris', json={'film_id': id, 'user_id': user_id})
        if response.status_code == 201:
            flash('Film ajouté aux favoris!', 'success')
        elif response.status_code == 409:
            flash('Ce film est déjà dans vos favoris', 'info')
        else:
            error_data = response.json()
            flash(error_data.get('error', 'Erreur lors de l\'ajout aux favoris'), 'error')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('details_film', id=id))

@app.route('/films/<id>/favoris/supprimer', methods=['POST'])
def supprimer_favori(id):
    if not is_authenticated():
        return redirect(url_for('login'))
    
    try:
        user_id = session.get('user_id')
        response = requests.delete(f'{API_URL}/api/favoris', json={'film_id': id, 'user_id': user_id})
        if response.status_code == 200:
            flash('Film retiré des favoris!', 'success')
        else:
            error_data = response.json()
            flash(error_data.get('error', 'Erreur'), 'error')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('details_film', id=id))

@app.route('/films/<id>/commenter', methods=['POST'])
def commenter_film(id):
    if not is_authenticated():
        return redirect(url_for('login'))
    
    try:
        user_id = session.get('user_id')
        note = request.form.get('note')
        commentaire = request.form.get('commentaire', '')
        
        if not note:
            flash('Veuillez saisir une note', 'error')
            return redirect(url_for('details_film', id=id))
        
        response = requests.post(f'{API_URL}/api/commentaires', json={
            'film_id': id,
            'user_id': user_id,
            'note': float(note),
            'commentaire': commentaire
        })
        
        if response.status_code == 201:
            flash('Commentaire ajouté avec succès!', 'success')
        else:
            error_data = response.json()
            flash(error_data.get('error', 'Erreur lors de l\'ajout du commentaire'), 'error')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('details_film', id=id))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
