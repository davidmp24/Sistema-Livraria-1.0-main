from flask import render_template, redirect, url_for, request, session, flash
from flask import Flask, jsonify
from config import app, db
from models import Cliente, Livro, Venda  # Certifique-se de que Livro está importado corretamente
from datetime import datetime
import os
import requests
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from config import app, db  # Certifique-se de que 'app' e 'db' estão importados corretamente

migrate = Migrate(app, db)

# Simulação de dados de login (usuário e senha)
USERS = {
    'admin': '123'  # Substitua por uma senha real
}
# HOME

@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

# FIM HOME
#####################################

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if USERS.get(username) == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Credenciais inválidas')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# FIM LOGIN
#########################################

# CLIENTES
@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if request.method == 'POST':
        nome_completo = request.form['nome_completo']
        data_nascimento = request.form['data_nascimento']
        identidade = request.form['identidade']
        telefone = request.form['telefone']
        email = request.form['email'] 
        rua = request.form['rua']
        cep = request.form['cep']  # Adicionando o campo 'cep'
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        profissao = request.form['profissao']
        escolaridade = request.form['escolaridade']

        novo_cliente = Cliente(
            nome_completo=nome_completo,
            data_nascimento=data_nascimento,
            identidade=identidade,
            telefone=telefone,
            email=email,
            rua=rua,
            cep=cep,  # Salvando o 'cep' no banco de dados
            bairro=bairro,
            cidade=cidade,
            profissao=profissao,
            escolaridade=escolaridade
        )

        try:
            db.session.add(novo_cliente)
            db.session.commit()
            flash('Cliente cadastrado com sucesso!')
            return redirect(url_for('clientes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar cliente: {str(e)}')
            return redirect(url_for('clientes'))
    else:
        nome = request.args.get('nome', '')
        if nome:
            clientes = Cliente.query.filter(Cliente.nome_completo.ilike(f'%{nome}%')).all()
        else:
            clientes = Cliente.query.all()

    return render_template('clientes.html', clientes=clientes, filter_name=nome)

@app.route('/novo_cliente')
def novo_cliente():
    return render_template('novo_cliente.html')

@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    
    if request.method == 'POST':
        cliente.nome_completo = request.form['nome_completo']
        cliente.data_nascimento = request.form['data_nascimento']
        cliente.identidade = request.form['identidade']
        cliente.telefone = request.form['telefone']
        cliente.rua = request.form['rua']
        cliente.cep = request.form['cep']  # Atualizando o campo 'cep'
        cliente.bairro = request.form['bairro']
        cliente.cidade = request.form['cidade']
        cliente.profissao = request.form['profissao']
        cliente.escolaridade = request.form['escolaridade']

        try:
            db.session.commit()
            flash('Cliente atualizado com sucesso!')
            return redirect(url_for('clientes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar cliente: {str(e)}')
            return redirect(url_for('clientes'))

    return render_template('editar_cliente.html', cliente=cliente)

@app.route('/deletar_cliente/<int:id>', methods=['POST'])
def deletar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    try:
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente excluído com sucesso!')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir cliente: {str(e)}')
    return redirect(url_for('clientes'))

@app.route('/cliente/<int:id>')
def visualizar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    return render_template('detalhes_cliente.html', cliente=cliente)

@app.route('/buscar_endereco', methods=['GET'])
def buscar_endereco():
    cep = request.args.get('cep')
    if cep:
        # Remover caracteres não numéricos do CEP
        cep = ''.join(filter(str.isdigit, cep))
        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'rua': data.get('logradouro', ''),
                'bairro': data.get('bairro', ''),
                'cidade': data.get('localidade', '')
            })
        else:
            return jsonify({'error': 'CEP não encontrado'}), 404

    return jsonify({'error': 'CEP inválido'}), 400
    
@app.route('/cliente/<int:id>', methods=['GET'])
def detalhes_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    
    cliente_data = {
        'id': cliente.id,
        'nome_completo': cliente.nome_completo,
        'data_nascimento': cliente.data_nascimento.strftime('%d/%m/%Y'),
        'identidade': cliente.identidade,
        'telefone': cliente.telefone,
        'rua': cliente.rua,
        'cep': cliente.cep,  # Incluindo 'cep' nos detalhes do cliente
        'bairro': cliente.bairro,
        'cidade': cliente.cidade,
        'profissao': cliente.profissao,
        'escolaridade': cliente.escolaridade
    }

    return jsonify(cliente_data)


# FIM CLIENTES
#########################################

# LIVROS
@app.route('/livros')
def livros():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Recupera todos os livros do banco de dados
    livros = Livro.query.all()

    return render_template('livros.html', livros=livros)


@app.route('/livro/<int:id>')
def visualizar_livro(id):
    livro = Livro.query.get_or_404(id)
    return render_template('detalhes_livro.html', livro=livro)


# Define o diretório para salvar as capas dos livros
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Rota para editar o livro
@app.route('/editar_livro/<int:id>', methods=['GET', 'POST'])
def editar_livro(id):
    livro = Livro.query.get_or_404(id)
    
    if request.method == 'POST':
        # Atualiza os dados do livro com base nos valores do formulário
        livro.titulo = request.form['titulo']
        livro.autor = request.form['autor']
        livro.editora = request.form['editora']
        livro.idade_leitura = request.form['idade_leitura']  # Atualizado de 'idade_leitura' para 'genero'
        livro.isbn = request.form['isbn']
        livro.ano = request.form['ano']
        livro.num_paginas = request.form['num_paginas']
        livro.valor = request.form['valor']
        livro.estoque = request.form['estoque']
        livro.capa_livro = request.form.get('capa_livro')  # Atualiza a URL da capa do livro

        try:
            db.session.commit()  # Salva as alterações no banco de dados
            flash('Livro atualizado com sucesso!', 'success')
            return redirect(url_for('livros'))  # Redireciona para a página de listagem de livros
        except SQLAlchemyError as e:
            db.session.rollback()  # Desfaz as alterações em caso de erro
            flash(f'Erro ao atualizar o livro: {str(e)}', 'danger')
            return redirect(url_for('editar_livro', id=id))

    return render_template('editar_livro.html', livro=livro)

# Rota para deletar o livro
@app.route('/deletar_livro/<int:id>', methods=['POST'])
def deletar_livro(id):
    livro = Livro.query.get_or_404(id)
    db.session.delete(livro)
    db.session.commit()
    return redirect(url_for('livros'))


# Rota para criar um novo livro
@app.route('/novo_livro', methods=['GET', 'POST'])
def novo_livro():
    if request.method == 'POST':
        # Pegar os dados do formulário
        titulo = request.form['titulo']
        autor = request.form['autor']
        editora = request.form['editora']
        idade_leitura = request.form.get('idade_leitura')  # Atualizado de 'idade_leitura' para 'genero'
        isbn = request.form['isbn']
        ano = request.form['ano']
        num_paginas = request.form['num_paginas']
        valor = request.form['valor']
        estoque = request.form['estoque']

        # Pegar a URL da capa do livro (enviada via campo oculto no formulário)
        capa_livro_url = request.form.get('capa_livro')  # Buscando a URL da capa

        # Criar um novo objeto livro com os dados do formulário
        novo_livro = Livro(
            titulo=titulo,
            autor=autor,
            editora=editora,
            idade_leitura=idade_leitura,  # Atualizado para 'genero'
            isbn=isbn,
            ano=ano,
            num_paginas=num_paginas,
            valor=valor,
            estoque=estoque,
            capa_livro=capa_livro_url  # Armazena a URL da capa do livro
        )

        # Adicionar e comitar no banco de dados
        db.session.add(novo_livro)
        db.session.commit()

        return redirect(url_for('livros'))

    return render_template('novo_livro.html')


# Rota para atualizar o livro no banco de dados
@app.route('/atualizar_livro/<int:livro_id>', methods=['POST'])
def atualizar_livro(livro_id):
    livro = Livro.query.get_or_404(livro_id)

    # Atualizar os dados do livro com base no formulário
    livro.titulo = request.form['titulo']
    livro.autor = request.form['autor']
    livro.editora = request.form['editora']
    livro.idade_leitura = request.form['idade_leitura']
    livro.isbn = request.form['isbn']
    livro.ano = request.form['ano']
    livro.num_paginas = request.form['num_paginas']
    livro.valor = request.form['valor']
    livro.estoque = request.form['estoque']

    try:
        db.session.commit()  # Salvar as alterações no banco de dados
        flash('Livro atualizado com sucesso!', 'success')
        return redirect(url_for('livros'))  # Redirecionar para a página de listagem de livros
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Erro ao atualizar o livro: {str(e)}', 'danger')
        return redirect(url_for('editar_livro', livro_id=livro_id))


# FIM LIVROS
#########################################

#VENDAS
#########################################
@app.route('/vendas', methods=['GET', 'POST'])
def vendas():
    livro_info = None
    if request.method == 'POST':
        livro_id = request.form.get('livro_id')

        # Buscar livro no banco de dados
        livro = Livro.query.get(livro_id)
        if livro:
            livro_info = {
                'capa': livro.capa_livro,
                'titulo': livro.titulo,
                'autor': livro.autor,
                'genero': livro.idade_leitura,  # ou outro campo referente ao gênero
                'estoque': livro.estoque,
                'valor': livro.valor
            }
        else:
            flash("Livro não encontrado", "danger")

    return render_template('vendas.html', livro_info=livro_info)

#Rota para buscar livro automatico
@app.route('/buscar_livro/<int:livro_id>', methods=['GET'])
def buscar_livro(livro_id):
    livro = Livro.query.get(livro_id)
    if livro:
        return jsonify({
            'capa': livro.capa_url,
            'titulo': livro.titulo,
            'autor': livro.autor,
            'idade_leitura': livro.idade_leitura,
            'estoque': livro.estoque,
            'valor': livro.preco
        })
    else:
        return jsonify(None), 404


#FIM#########################################################

# CONFIGURAÇÃO

@app.route('/configuracao')
def configuracao():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('configuracao.html')

# FIM CONFIGURAÇÃO
#########################################


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Certifique-se de que as tabelas estão sendo criadas
    app.run(debug=True)