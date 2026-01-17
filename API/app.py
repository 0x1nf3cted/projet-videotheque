from flask import Flask, send_from_directory
from flask_cors import CORS
from routes.auth import auth_bp
from routes.films import films_bp
from routes.acteurs import acteurs_bp
from routes.emprunts import emprunts_bp
from routes.favoris import favoris_bp
from routes.commentaires import commentaires_bp
import os

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
if not app.config['JWT_SECRET_KEY']:
    raise ValueError("JWT_SECRET_KEY n'est pas défini")

IMAGES_DIR = os.environ.get('IMAGES_DIR', '/app/images')
os.makedirs(IMAGES_DIR, exist_ok=True)

# Route pour servir les images
@app.route('/api/images/<filename>')
def serve_image(filename):
    """Sert les images depuis le répertoire d'images"""
    return send_from_directory(IMAGES_DIR, filename)

# tous nos route pour l'application 
app.register_blueprint(auth_bp)
app.register_blueprint(films_bp)
app.register_blueprint(acteurs_bp)
app.register_blueprint(emprunts_bp)
app.register_blueprint(favoris_bp)
app.register_blueprint(commentaires_bp)

from utils.json_handler import lire_json
films_existants = lire_json('films.json')
if not films_existants or len(films_existants) == 0:
    try:
        from seeder import seed
        seed()
    except Exception as e:
        print(f'Erreur lors du seeder: {e}')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
