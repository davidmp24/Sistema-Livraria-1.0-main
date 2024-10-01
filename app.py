from flask import render_template, redirect, url_for, request, session, flash
from flask import Flask, jsonify
from config import app, db
from models import Cliente, Livro  # Certifique-se de que Livro está importado corretamente
from datetime import datetime
import os
from werkzeug.utils import secure_filename

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
        rua = request.form['rua']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        profissao = request.form['profissao']
        escolaridade = request.form['escolaridade']

        novo_cliente = Cliente(
            nome_completo=nome_completo,
            data_nascimento=data_nascimento,
            identidade=identidade,
            telefone=telefone,
            rua=rua,
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

@app.route('/editar_livro/<int:id>', methods=['GET', 'POST'])
def editar_livro(id):
    livro = Livro.query.get_or_404(id)
    # Aqui você pode adicionar a lógica para editar o livro
    return render_template('editar_livro.html', livro=livro)

@app.route('/deletar_livro/<int:id>', methods=['POST'])
def deletar_livro(id):
    livro = Livro.query.get_or_404(id)  # Busca o livro pelo ID
    db.session.delete(livro)  # Deleta o livro da sessão
    db.session.commit()  # Confirma a transação
    return redirect(url_for('livros'))  # Redireciona para a lista de livros



# Rota para novo livro
@app.route('/novo_livro', methods=['GET', 'POST'])
def novo_livro():
    if request.method == 'POST':
        # Pegar os dados do formulário
        titulo = request.form['titulo']
        autor = request.form['autor']
        editora = request.form['editora']
        idade_leitura = request.form.get('idade_leitura')
        isbn = request.form['isbn']
        ano = request.form['ano']
        num_paginas = request.form['num_paginas']
        valor = request.form['valor']

        # Verifica se há uma capa de livro enviada
        capa_livro = request.files['capa_livro']
        capa_livro_filename = None
        if capa_livro:
            # Salva a capa com um nome seguro
            capa_livro_filename = secure_filename(capa_livro.filename)
            capa_livro.save(os.path.join(app.config['UPLOAD_FOLDER'], capa_livro_filename))

        # Cria um novo objeto livro com os dados do formulário
        novo_livro = Livro(
            titulo=titulo,
            autor=autor,
            editora=editora,
            idade_leitura=idade_leitura,
            isbn=isbn,
            ano=ano,
            num_paginas=num_paginas,
            valor=valor,
            capa_livro=capa_livro_filename  # Adiciona a capa ao livro
        )

        # Adiciona e comita no banco de dados
        db.session.add(novo_livro)
        db.session.commit()

        return redirect(url_for('livros'))

    return render_template('novo_livro.html')

# FIM LIVROS
#########################################

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
