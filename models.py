from config import db
from datetime import datetime

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.String(10), nullable=False)
    identidade = db.Column(db.String(50), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)  # Coluna telefone
    rua = db.Column(db.String(100), nullable=False)  # Coluna rua
    bairro = db.Column(db.String(100), nullable=False)  # Coluna bairro
    cidade = db.Column(db.String(50), nullable=False)
    profissao = db.Column(db.String(50), nullable=False)
    escolaridade = db.Column(db.String(50), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

