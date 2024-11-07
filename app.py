from flask import render_template, redirect, url_for, request, session, flash
from flask import Flask, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from config import app, db
from models import Cliente, Livro, Venda  # Certifique-se de que Livro está importado corretamente
from datetime import datetime
import os
import requests
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from config import app, db  # Certifique-se de que 'app' e 'db' estão importados corretamente
import logging

migrate = Migrate(app, db)

# Inicialização do LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# Definição do carregador de usuário
@login_manager.user_loader
def load_user(user_id):
    return username.query.get(int(user_id))  # Aqui, retorne o usuário correspondente ao ID

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


@app.route('/alterar_senha', methods=['GET', 'POST'])
def alterar_senha():
    # Verifica se o usuário está autenticado
    if 'username' not in session:
        flash('Você precisa estar logado para alterar a senha.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        nova_senha = request.form['nova_senha']
        confirmar_senha = request.form['confirmar_senha']

        if nova_senha == confirmar_senha:
            # Aqui você pode implementar a lógica para atualizar a senha do usuário
            # No seu caso, se estiver usando um dicionário USERS:
            USERS[session['username']] = nova_senha
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('home'))  # Redireciona para a página inicial
        else:
            flash('As senhas não conferem. Tente novamente.', 'danger')

    return render_template('alterar_senha.html')

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
logging.basicConfig(level=logging.DEBUG)

@app.route('/vendas', methods=['GET', 'POST'])
def vendas():
    livro_info = None
    if request.method == 'POST':
        livro_id = request.form.get('livro_id')

        # Buscar livro no banco de dados
        with db.session() as session:
          livro = session.get(Livro, livro_id)

        if livro:
            livro_info = {
                'capa': livro.capa_livro,
                'id': livro.id,
                'titulo': livro.titulo,
                'autor': livro.autor,
                'genero': livro.idade_leitura,  # ou outro campo referente ao gênero
                'estoque': livro.estoque,
                'valor': livro.valor
            }
        else:
            flash("Livro não encontrado", "danger")

    return render_template('vendas.html', livro_info=livro_info)

@app.route('/confirmar_venda', methods=['POST'])
def confirmar_venda():
    logging.debug("Recebendo solicitação para confirmar venda...")
    
    data = request.get_json()  # Recebendo os dados JSON
    if not data:
        logging.error("Nenhum dado foi enviado na solicitação.")
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    # Extraindo os dados
    livro_id = data.get('livro_id')
    quantidade = data.get('quantidade')
    valor_total = data.get('valor_total')
    cliente_info = data.get('cliente_info')

    logging.debug(f"Dados recebidos: {data}")

    # Verificando se todos os campos estão presentes
    if not livro_id or not quantidade or not valor_total or not cliente_info:
        logging.error("Dados ausentes na solicitação.")
        return jsonify({'success': False, 'error': 'Missing data'}), 400

    # Buscar o cliente pelo info (pode ser CPF ou outro identificador)
    cliente = Cliente.query.filter((Cliente.identidade == cliente_info) | (Cliente.email == cliente_info)).first()
    if not cliente:
        logging.error(f"Cliente não encontrado para o info: {cliente_info}")
        return jsonify({'success': False, 'error': 'Cliente not found'}), 400

    # Buscar o livro
    livro = Livro.query.get(livro_id)
    if not livro:
        logging.error(f"Livro não encontrado com ID: {livro_id}")
        return jsonify({'success': False, 'error': 'Livro not found'}), 400

    # Verificando a quantidade em estoque
    if quantidade > livro.estoque:
        logging.error(f"Quantidade solicitada: {quantidade} excede o estoque disponível: {livro.estoque}")
        return jsonify({'success': False, 'error': 'Insufficient stock'}), 400

    # Criar a venda
    nova_venda = Venda(
        cliente_id=cliente.id,
        livro_id=livro_id,
        data_venda=datetime.utcnow(),
        valor_pago=livro.valor,
        quantidade_vendida=quantidade,
        valor_total=valor_total,

    )

    # Adicionar a venda ao banco de dados
    db.session.add(nova_venda)
    livro.estoque -= quantidade  # Atualizar o estoque do livro
    db.session.commit()

    logging.debug(f"Venda confirmada com sucesso! ID da venda: {nova_venda.id}")
    return jsonify({'success': True, 'venda_id': nova_venda.id}), 200


# Rota Buscar Cliente
@app.route('/buscar_cliente', methods=['GET'])
def buscar_cliente():
    info = request.args.get('info', '')
    clientes = Cliente.query.filter(
        (Cliente.nome_completo.ilike(f'%{info}%')) | 
        (Cliente.identidade.ilike(f'%{info}%'))
    ).all()

    if clientes:
        return jsonify(success=True, clientes=[{'nome_completo': c.nome_completo, 'identidade': c.identidade} for c in clientes])
    else:
        return jsonify(success=False, clientes=[])
        
#Rota extrato de venda
@app.route('/extrato_venda/<int:venda_id>', methods=['GET'])
def extrato_venda(venda_id):
    venda = Venda.query.get_or_404(venda_id)
    return render_template('extrato_venda.html', venda=venda)


#Rota para buscar livro automatico
@app.route('/buscar_livro/<int:livro_id>')
def buscar_livro(livro_id):
    with db.session() as session:
        livro = session.get(Livro, livro_id)
    if livro:
        return jsonify({
            'capa': livro.capa_url,
            'id': livro.id,
            'titulo': livro.titulo,
            'autor': livro.autor,
            'idade_leitura': livro.idade_leitura,
            'estoque': livro.estoque,
            'valor': livro.preco
        })
    else:
        return jsonify(None), 404

@app.route('/atualizar_venda', methods=['POST'])
def atualizar_venda():
    data = request.get_json()
    venda_id = data['venda_id']
    valor_pago = data['valor_pago']

    # Atualizar a venda no banco de dados
    venda = Venda.query.get(venda_id)
    if venda:
        venda.valor_pago = valor_pago
        db.session.commit()
        return {'message': 'Venda atualizada com sucesso'}, 200
    return {'message': 'Venda não encontrada'}, 404

from flask import request

@app.route('/controle_caixa', methods=['GET'])
def controle_caixa():
    cliente = request.args.get('cliente')
    titulo = request.args.get('titulo')
    data = request.args.get('data')

    query = Venda.query

    # Filtros aplicados à consulta de vendas
    if cliente:
        query = query.join(Cliente).filter(Cliente.nome_completo.ilike(f"%{cliente}%"))
    if titulo:
        query = query.join(Livro).filter(Livro.titulo.ilike(f"%{titulo}%"))
    if data:
        query = query.filter(Venda.data_venda.contains(data))  # Ajuste para data conforme necessário

    vendas = query.all()

    return render_template('controle_caixa.html', vendas=vendas)

#FIM#########################################################

#CONTROLE DE CAIXA ##########################################

@app.template_filter('currency')
def currency_filter(value):
    """Formata um número como moeda brasileira."""
    return f"R$ {value:.2f}".replace('.', ',')
#FIM ########################################################

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
