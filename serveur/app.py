from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
API_URL = os.environ.get('API_URL', 'http://localhost:5001')

def is_authenticated():
    return 'token' in session and session.get('token')

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
            
            # on récupère les acteurs du film
            acteurs = []
            acteurs_ids = film.get('acteurs', [])
            if acteurs_ids:
                response_acteurs = requests.get(f'{API_URL}/api/acteurs')
                if response_acteurs.status_code == 200:
                    acteurs_data = response_acteurs.json()
                    tous_acteurs = acteurs_data.get('data', [])
                    # on filtre seulement les acteurs qui sont dans ce film
                    acteurs = [a for a in tous_acteurs if a.get('id') in acteurs_ids]
            
            return render_template('films/details.html', film=film, acteurs=acteurs)
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
