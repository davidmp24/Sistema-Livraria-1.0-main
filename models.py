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


class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    editora = db.Column(db.String(100), nullable=False)
    idade_leitura = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    num_paginas = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    capa_livro = db.Column(db.String(200), nullable=True)  # Novo campo para a capa

    def __init__(self, titulo, autor, editora, idade_leitura, isbn, ano, num_paginas, valor, capa_livro):
        self.titulo = titulo
        self.autor = autor
        self.editora = editora
        self.idade_leitura = idade_leitura
        self.isbn = isbn
        self.ano = ano
        self.num_paginas = num_paginas
        self.valor = valor
        self.capa_livro = capa_livro