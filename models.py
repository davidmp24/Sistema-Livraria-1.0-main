from config import db
from datetime import datetime
from sqlalchemy import Float  # Certifique-se de importar o tipo Float


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.String(10), nullable=False)
    identidade = db.Column(db.String(50), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)  # Coluna telefone
    email = db.Column(db.String(100), nullable=False) 
    rua = db.Column(db.String(100), nullable=False)  # Coluna rua
    cep = db.Column(db.String(9), nullable=False)
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
    capa_livro = db.Column(db.String(200), nullable=True) 
    estoque = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Livro {self.titulo}>'

    def __init__(self, titulo, autor, editora, idade_leitura, isbn, ano, num_paginas, valor, capa_livro, estoque):
        self.titulo = titulo
        self.autor = autor
        self.editora = editora
        self.idade_leitura = idade_leitura
        self.isbn = isbn
        self.ano = ano
        self.num_paginas = num_paginas
        self.valor = valor
        self.capa_livro = capa_livro
        self.estoque = estoque


class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'), nullable=False)
    data_venda = db.Column(db.DateTime, default=datetime.utcnow)
    valor_pago = db.Column(Float)
    quantidade_vendida = db.Column(db.Integer, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)

    # Relacionamentos
    cliente = db.relationship('Cliente', backref=db.backref('vendas', lazy=True))
    livro = db.relationship('Livro', backref=db.backref('vendas', lazy=True))

    def __repr__(self):
        # Acessando o título do livro através da relação livro
        return f'<Venda {self.id} - Cliente: {self.cliente.nome_completo} - Livro: {self.livro.titulo} - Quantidade: {self.quantidade_vendida}>'
        

def init_db(app):
    with app.app_context():
        db.create_all()