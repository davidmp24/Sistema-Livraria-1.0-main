from flask import render_template, redirect, url_for, request, session, flash
from config import app, db
from models import Cliente
from flask import jsonify
from datetime import datetime

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

# LOGUIN
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

#FIM LOGUIN
#########################################

#CLIENTES
@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    # Verifica se o método é POST (tentativa de cadastro)
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

        # Cria um novo objeto cliente
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
            db.session.add(novo_cliente)  # Adiciona o cliente ao banco
            db.session.commit()  # Confirma a transação
            flash('Cliente cadastrado com sucesso!')
            return redirect(url_for('clientes'))  # Redireciona para a mesma rota após o cadastro
        except Exception as e:
            db.session.rollback()  # Reverte em caso de erro
            flash(f'Erro ao cadastrar cliente: {str(e)}')
            return redirect(url_for('clientes'))

    # Lógica de filtro (GET request) para buscar clientes pelo nome
    else:
        # Para o método GET, verifica se há um parâmetro de pesquisa
        nome = request.args.get('nome', '')
        if nome:
            clientes = Cliente.query.filter(Cliente.nome_completo.ilike(f'%{nome}%')).all()
        else:
            clientes = Cliente.query.all()
        
    return render_template('clientes.html', clientes=clientes, filter_name=nome)


# Rota para adicionar um novo cliente
@app.route('/novo_cliente')
def novo_cliente():
    return render_template('novo_cliente.html')


# Rota para editar um cliente
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

# Rota para excluir um cliente
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

# Rota para pesquisar clientes
@app.route('/cliente/<int:id>')
def visualizar_cliente(id):
    cliente = Cliente.query.get_or_404(id)  # Busca o cliente pelo ID ou retorna 404 se não encontrar
    return render_template('detalhes_cliente.html', cliente=cliente)

@app.route('/cliente/<int:id>', methods=['GET'])
def detalhes_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    
    cliente_data = {
        'id': cliente.id,
        'nome_completo': cliente.nome_completo,
        'data_nascimento': cliente.data_nascimento.strftime('%d/%m/%Y'),  # Formatar a data
        'identidade': cliente.identidade,
        'telefone': cliente.telefone,
        'rua': cliente.rua,
        'bairro': cliente.bairro,
        'cidade': cliente.cidade,
        'profissao': cliente.profissao,
        'escolaridade': cliente.escolaridade
    }

    return jsonify(cliente_data)

#FIM CLIENTES
#########################################

#LIVROS
@app.route('/livros')
def livros():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('livros.html')

#Rota para novo livro
@app.route('/novo_livro', methods=['GET', 'POST'])
def novo_livro():
    if request.method == 'POST':
        # Pegar os dados do formulário
        titulo = request.form['titulo']
        autor = request.form['autor']
        editora = request.form['editora']
        ano = request.form['ano']
        isbn = request.form['isbn']

        # Código para salvar o livro no banco de dados
        novo_livro = Livro(titulo=titulo, autor=autor, editora=editora, ano=ano, isbn=isbn)
        db.session.add(novo_livro)
        db.session.commit()

        return redirect(url_for('livros'))

    return render_template('novo_livro.html')

# Rota para criar novo livro
@app.route('/novo_livro', methods=['GET', 'POST'])
def criar_livro():
    if request.method == 'POST':
        # Pegar os dados do formulário
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano = request.form['ano']
        isbn = request.form['isbn']

        # Código para salvar o livro no banco de dados
        novo_livro = Livro(titulo=titulo, autor=autor, ano=ano, isbn=isbn)
        db.session.add(novo_livro)
        db.session.commit()
        data = request.get_json()
        return jsonify(success=True), 201
    return redirect(url_for('livros'))
    print(request.form)

    return render_template('novo_livro.html')


#FIM LIVROS
#########################################
#CONFIGURAÇAO

@app.route('/configuracao')
def configuracao():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('configuracao.html')

#FIM CONFIGURAÇAO
#########################################


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Certifique-se de que as tabelas estão sendo criadas
    app.run(debug=True)    