from flask import Flask
from flask_cors import CORS
from routes.auth import auth_bp
from routes.films import films_bp
from routes.acteurs import acteurs_bp
import os

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
if not app.config['JWT_SECRET_KEY']:
    raise ValueError("JWT_SECRET_KEY n'est pas défini")
app.register_blueprint(auth_bp)
app.register_blueprint(films_bp)
app.register_blueprint(acteurs_bp)

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
