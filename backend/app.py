from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
import psycopg2


#importar url do banco de dados
from config.config import DATABASE_URL, SECRET_KEY

# Importe a função de configuração da API
from model.model_config import configure_api

# Configure a API ao iniciar o app
configure_api()

app = Flask(__name__)
app.config.update(SECRET_KEY = SECRET_KEY)
CORS(app, resources={r"/ask": {"origins": "http://localhost:8080"}})

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# conectar ao banco de dados
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

from routes import * 

if __name__ == '__main__':
    app.run(debug=True)

