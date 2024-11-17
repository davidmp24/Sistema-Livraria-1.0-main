from flask import render_template, redirect, url_for, request, session, flash
from flask import Flask, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from config import app, db
from models import Cliente, Livro, Venda  
from datetime import datetime, timedelta, timezone
import os
import requests
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from config import app, db  
import logging
from sqlalchemy import func

migrate = Migrate(app, db)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return username.query.get(int(user_id))  


USERS = {
    'admin': '123'  
}


@app.route('/')
def home():
    if 'username' in session:
        
        vendas = Venda.query.all()  
        
        
        vendas_dia_total = calcular_vendas_dia_total()
        print("Vendas do Dia Total:", vendas_dia_total)  

        vendas_dia_quantidade = db.session.query(db.func.count(Venda.id)).filter(db.func.date(Venda.data_venda) == datetime.today().date()).scalar() or 0
        vendas_semana_total = calcular_vendas_semana_total()
        vendas_semana_quantidade = db.session.query(db.func.count(Venda.id)).filter(Venda.data_venda >= datetime.today() - timedelta(days=datetime.today().weekday())).scalar() or 0
        
        vendas_dia_labels = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
        vendas_dia_dados = [20, 15, 30, 25, 40, 10, 50]
        vendas_semana_labels = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        vendas_semana_dados = [100, 120, 150, 200, 180, 160, 140]
        
        return render_template('index.html', 
                               vendas=vendas,
                               vendas_dia_total=vendas_dia_total,
                               vendas_dia_quantidade=vendas_dia_quantidade,
                               vendas_semana_total=vendas_semana_total,
                               vendas_semana_quantidade=vendas_semana_quantidade,
                               vendas_dia_labels=vendas_dia_labels,
                               vendas_dia_dados=vendas_dia_dados,
                               vendas_semana_labels=vendas_semana_labels,
                               vendas_semana_dados=vendas_semana_dados)
    return redirect(url_for('login'))





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
    
    if 'username' not in session:
        flash('Você precisa estar logado para alterar a senha.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        nova_senha = request.form['nova_senha']
        confirmar_senha = request.form['confirmar_senha']

        if nova_senha == confirmar_senha:
            
            
            USERS[session['username']] = nova_senha
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('home'))  
        else:
            flash('As senhas não conferem. Tente novamente.', 'danger')

    return render_template('alterar_senha.html')





@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if request.method == 'POST':
        nome_completo = request.form['nome_completo']
        data_nascimento = request.form['data_nascimento']
        identidade = request.form['identidade']
        telefone = request.form['telefone']
        email = request.form['email'] 
        rua = request.form['rua']
        cep = request.form['cep']  
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
            cep=cep,  
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
        cliente.cep = request.form['cep']  
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
        'cep': cliente.cep,  
        'bairro': cliente.bairro,
        'cidade': cliente.cidade,
        'profissao': cliente.profissao,
        'escolaridade': cliente.escolaridade
    }

    return jsonify(cliente_data)






@app.route('/livros')
def livros():
    if 'username' not in session:
        return redirect(url_for('login'))

    
    livros = Livro.query.all()

    return render_template('livros.html', livros=livros)


@app.route('/livro/<int:id>')
def visualizar_livro(id):
    livro = Livro.query.get_or_404(id)
    return render_template('detalhes_livro.html', livro=livro)



UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/editar_livro/<int:id>', methods=['GET', 'POST'])
def editar_livro(id):
    livro = Livro.query.get_or_404(id)
    
    if request.method == 'POST':
        
        livro.titulo = request.form['titulo']
        livro.autor = request.form['autor']
        livro.editora = request.form['editora']
        livro.idade_leitura = request.form['idade_leitura']  
        livro.isbn = request.form['isbn']
        livro.ano = request.form['ano']
        livro.num_paginas = request.form['num_paginas']
        livro.valor = request.form['valor']
        livro.estoque = request.form['estoque']
        livro.capa_livro = request.form.get('capa_livro')  

        try:
            db.session.commit()  
            flash('Livro atualizado com sucesso!', 'success')
            return redirect(url_for('livros'))  
        except SQLAlchemyError as e:
            db.session.rollback()  
            flash(f'Erro ao atualizar o livro: {str(e)}', 'danger')
            return redirect(url_for('editar_livro', id=id))

    return render_template('editar_livro.html', livro=livro)


@app.route('/deletar_livro/<int:id>', methods=['POST'])
def deletar_livro(id):
    livro = Livro.query.get_or_404(id)
    db.session.delete(livro)
    db.session.commit()
    return redirect(url_for('livros'))



@app.route('/novo_livro', methods=['GET', 'POST'])
def novo_livro():
    if request.method == 'POST':
        
        titulo = request.form['titulo']
        autor = request.form['autor']
        editora = request.form['editora']
        idade_leitura = request.form.get('idade_leitura')  
        isbn = request.form['isbn']
        ano = request.form['ano']
        num_paginas = request.form['num_paginas']
        valor = request.form['valor']
        estoque = request.form['estoque']

        
        capa_livro_url = request.form.get('capa_livro')  

        
        novo_livro = Livro(
            titulo=titulo,
            autor=autor,
            editora=editora,
            idade_leitura=idade_leitura,  
            isbn=isbn,
            ano=ano,
            num_paginas=num_paginas,
            valor=valor,
            estoque=estoque,
            capa_livro=capa_livro_url  
        )

        
        db.session.add(novo_livro)
        db.session.commit()

        return redirect(url_for('livros'))

    return render_template('novo_livro.html')



@app.route('/atualizar_livro/<int:livro_id>', methods=['POST'])
def atualizar_livro(livro_id):
    livro = Livro.query.get_or_404(livro_id)

    
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
        db.session.commit()  
        flash('Livro atualizado com sucesso!', 'success')
        return redirect(url_for('livros'))  
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Erro ao atualizar o livro: {str(e)}', 'danger')
        return redirect(url_for('editar_livro', livro_id=livro_id))







logging.basicConfig(level=logging.DEBUG)

@app.route('/vendas', methods=['GET', 'POST'])
def vendas():
    livro_info = None
    if request.method == 'POST':
        livro_id = request.form.get('livro_id')

        
        with db.session() as session:
          livro = session.get(Livro, livro_id)

        if livro:
            livro_info = {
                'capa': livro.capa_livro,
                'id': livro.id,
                'titulo': livro.titulo,
                'autor': livro.autor,
                'genero': livro.idade_leitura,  
                'estoque': livro.estoque,
                'valor': livro.valor
            }
        else:
            flash("Livro não encontrado", "danger")

    return render_template('vendas.html', livro_info=livro_info)

@app.route('/confirmar_venda', methods=['POST'])
def confirmar_venda():
    logging.debug("Recebendo solicitação para confirmar venda...")
    
    data = request.get_json()  
    if not data:
        logging.error("Nenhum dado foi enviado na solicitação.")
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    
    livro_id = data.get('livro_id')
    quantidade = data.get('quantidade')
    valor_total = data.get('valor_total')
    cliente_info = data.get('cliente_info')

    logging.debug(f"Dados recebidos: {data}")

    
    if not livro_id or not quantidade or not valor_total or not cliente_info:
        logging.error("Dados ausentes na solicitação.")
        return jsonify({'success': False, 'error': 'Missing data'}), 400

    
    cliente = Cliente.query.filter((Cliente.identidade == cliente_info) | (Cliente.email == cliente_info)).first()
    if not cliente:
        logging.error(f"Cliente não encontrado para o info: {cliente_info}")
        return jsonify({'success': False, 'error': 'Cliente not found'}), 400

    
    livro = Livro.query.get(livro_id)
    if not livro:
        logging.error(f"Livro não encontrado com ID: {livro_id}")
        return jsonify({'success': False, 'error': 'Livro not found'}), 400

    
    if quantidade > livro.estoque:
        logging.error(f"Quantidade solicitada: {quantidade} excede o estoque disponível: {livro.estoque}")
        return jsonify({'success': False, 'error': 'Insufficient stock'}), 400

    
    nova_venda = Venda(
        cliente_id=cliente.id,
        livro_id=livro_id,
        data_venda=datetime.utcnow(),
        valor_pago=livro.valor,
        quantidade_vendida=quantidade,
        valor_total=valor_total,

    )

    
    db.session.add(nova_venda)
    livro.estoque -= quantidade  
    db.session.commit()

    logging.debug(f"Venda confirmada com sucesso! ID da venda: {nova_venda.id}")
    return jsonify({'success': True, 'venda_id': nova_venda.id}), 200



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
        

@app.route('/extrato_venda/<int:venda_id>', methods=['GET'])
def extrato_venda(venda_id):
    venda = Venda.query.get_or_404(venda_id)
    return render_template('extrato_venda.html', venda=venda)



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

    
    if cliente:
        query = query.join(Cliente).filter(Cliente.nome_completo.ilike(f"%{cliente}%"))
    if titulo:
        query = query.join(Livro).filter(Livro.titulo.ilike(f"%{titulo}%"))
    if data:
        query = query.filter(Venda.data_venda.contains(data))  

    vendas = query.all()

    return render_template('controle_caixa.html', vendas=vendas)





@app.template_filter('currency')
def currency_filter(value):
    """Formata um número como moeda brasileira."""
    return f"R$ {value:.2f}".replace('.', ',')




@app.route('/configuracao')
def configuracao():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('configuracao.html')




@app.route('/relatorio-vendas')
def relatorio_vendas():
    
    vendas = Venda.query.join(Cliente).all()  
       
  
    vendas_dia = db.session.query(Venda).filter(Venda.data_venda == datetime.now(timezone.utc).date()).all()
    vendas_semana = db.session.query(Venda).filter(Venda.data_venda >= datetime.now(timezone.utc) - timedelta(weeks=1)).all()
    
    
    vendas_dia_total = sum([v.valor_total for v in vendas_dia])
    vendas_semana_total = sum([v.valor_total for v in vendas_semana])

    return render_template('relatorio_vendas.html', vendas=vendas, vendas_dia=vendas_dia, vendas_semana=vendas_semana,
                           vendas_dia_total=vendas_dia_total, vendas_semana_total=vendas_semana_total)



def calcular_vendas_dia_total():
    hoje = datetime.today().date()
    total_dia = db.session.query(db.func.sum(Venda.valor_total)).filter(db.func.date(Venda.data_venda) == hoje).scalar()
    return total_dia if total_dia is not None else 0.0


vendas_dia_quantidade = db.session.query(db.func.count(Venda.id)).filter(db.func.date(Venda.data_venda) == datetime.today().date()).scalar() or 0


def calcular_vendas_semana_total():
    inicio_semana = datetime.today() - timedelta(days=datetime.today().weekday())
    total_semana = db.session.query(db.func.sum(Venda.valor_total)).filter(Venda.data_venda >= inicio_semana).scalar()
    return total_semana if total_semana is not None else 0.0


vendas_semana_quantidade = db.session.query(db.func.count(Venda.id)).filter(Venda.data_venda >= datetime.today() - timedelta(days=datetime.today().weekday())).scalar() or 0

@app.route('/dashboard')
def dashboard():
    
    vendas_dia_total = calcular_vendas_dia_total()  
    vendas_dia_quantidade = db.session.query(db.func.count(Venda.id)).filter(db.func.date(Venda.data_venda) == datetime.today().date()).scalar() or 0

    
    vendas_semana_total = calcular_vendas_semana_total()  
    vendas_semana_quantidade = db.session.query(db.func.count(Venda.id)).filter(Venda.data_venda >= datetime.today() - timedelta(days=datetime.today().weekday())).scalar() or 0

    
    vendas_dia_labels = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']  
    vendas_dia_dados = [20, 15, 30, 25, 40, 10, 50]  
    vendas_semana_labels = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']  
    vendas_semana_dados = [100, 120, 150, 200, 180, 160, 140]  

    
    return render_template('dashboard.html',
                           vendas_dia_total=vendas_dia_total,
                           vendas_dia_quantidade=vendas_dia_quantidade,
                           vendas_semana_total=vendas_semana_total,
                           vendas_semana_quantidade=vendas_semana_quantidade,
                           vendas_dia_labels=vendas_dia_labels,
                           vendas_dia_dados=vendas_dia_dados,
                           vendas_semana_labels=vendas_semana_labels,
                           vendas_semana_dados=vendas_semana_dados)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
