from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Substitua por uma chave secreta real
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clientes.db'  # Caminho para o banco de dados SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
