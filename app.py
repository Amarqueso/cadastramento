from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Substitua por uma chave secreta real

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'cadastros.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de dados com novos campos
class Cadastro(db.Model):
    __tablename__ = 'cadastro'  # Explicitamente define o nome da tabela
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    pretensao = db.Column(db.String(50), nullable=False)  # Alugar, vender, comprar
    tipo_imovel = db.Column(db.String(50), nullable=False)  # Casa, apartamento
    quartos = db.Column(db.Integer, nullable=False)
    vagas = db.Column(db.Integer, nullable=False)
    suites = db.Column(db.Integer, nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Cadastro {self.nome}>'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    try:
        nome = request.form['nome']
        telefone = request.form['telefone']
        email = request.form['email']
        pretensao = request.form['pretensao']
        tipo_imovel = request.form['tipo_imovel']
        quartos = int(request.form['quartos'])
        vagas = int(request.form['vagas'])
        suites = int(request.form['suites'])

        novo_cadastro = Cadastro(
            nome=nome,
            telefone=telefone,
            email=email,
            pretensao=pretensao,
            tipo_imovel=tipo_imovel,
            quartos=quartos,
            vagas=vagas,
            suites=suites
        )
        db.session.add(novo_cadastro)
        db.session.commit()
        return redirect('/cadastros')
    except Exception as e:
        return f'Erro ao cadastrar: {e}'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == '12345678':
            session['admin'] = True
            return redirect(url_for('cadastros'))
        else:
            return 'Credenciais inválidas!'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

@app.route('/cadastros', methods=['GET', 'POST'])
def cadastros():
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    try:
        if request.method == 'POST':
            nome_busca = request.form.get('nome_busca', '')
            todos_cadastros = Cadastro.query.filter(Cadastro.nome.ilike(f'%{nome_busca}%')).order_by(Cadastro.data_hora.desc()).all()
        else:
            todos_cadastros = Cadastro.query.order_by(Cadastro.data_hora.desc()).all()
        
        for cadastro in todos_cadastros:
            cadastro.data_hora = cadastro.data_hora.strftime('%d/%m/%Y %H:%M:%S')
            
        return render_template('cadastros.html', cadastros=todos_cadastros)
    except Exception as e:
        return f'Erro ao exibir cadastros: {e}'

@app.route('/download')
def download():
    if 'admin' not in session:
        return redirect(url_for('login'))

    try:
        cadastros = Cadastro.query.all()
        data = {
            'Nome': [c.nome for c in cadastros],
            'Telefone': [c.telefone for c in cadastros],
            'Email': [c.email for c in cadastros],
            'Pretensão': [c.pretensao for c in cadastros],
            'Tipo de Imóvel': [c.tipo_imovel for c in cadastros],
            'Quartos': [c.quartos for c in cadastros],
            'Vagas': [c.vagas for c in cadastros],
            'Suítes': [c.suites for c in cadastros],
            'Data e Hora': [c.data_hora.strftime('%d/%m/%Y %H:%M:%S') for c in cadastros]
        }
        df = pd.DataFrame(data)
        path = os.path.join(app.instance_path, 'cadastros.xlsx')
        df.to_excel(path, index=False)

        return f'<a href="/download_excel">Baixar Excel</a>'
    except Exception as e:
        return f'Erro ao baixar os cadastros: {e}'

@app.route('/download_excel')
def download_excel():
    if 'admin' not in session:
        return redirect(url_for('login'))

    path = os.path.join(app.instance_path, 'cadastros.xlsx')
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
    
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f'Erro ao criar o banco de dados e tabelas: {e}')
    app.run(debug=True)
