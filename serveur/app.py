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
    return render_template('index.html', username=session.get('username'))

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
