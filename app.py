from flask import render_template, redirect, url_for, request, session, flash
from config import app, db
from models import Cliente

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

    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

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

@app.route('/cliente/<int:id>')
def visualizar_cliente(id):
    cliente = Cliente.query.get_or_404(id)  # Busca o cliente pelo ID ou retorna 404 se não encontrar
    return render_template('detalhes_cliente.html', cliente=cliente)

#FIM CLIENTES
#########################################

#LIVROS
@app.route('/livros')
def livros():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('livros.html')

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
        db.drop_all()
        db.create_all()   # Cria as tabelas no banco de dados
    app.run(debug=True)