from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Caminho para o banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/cadastro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definição do modelo de dados
class Cadastro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    pretensao = db.Column(db.String(20), nullable=False)
    tipo_imovel = db.Column(db.String(20), nullable=False)
    quartos = db.Column(db.Integer, nullable=False)
    vagas = db.Column(db.Integer, nullable=False)
    suites = db.Column(db.Integer, nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.now)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        email = request.form['email']
        pretensao = request.form['pretensao']
        tipo_imovel = request.form['tipo_imovel']
        quartos = request.form['quartos']
        vagas = request.form['vagas']
        suites = request.form['suites']
        data_hora = datetime.now()

        novo_cadastro = Cadastro(nome=nome, telefone=telefone, email=email, pretensao=pretensao,
                                 tipo_imovel=tipo_imovel, quartos=quartos, vagas=vagas, suites=suites,
                                 data_hora=data_hora)

        try:
            db.session.add(novo_cadastro)
            db.session.commit()
            return redirect(url_for('cadastrar'))
        except Exception as e:
            print(f"Erro ao cadastrar: {e}")
            return "Erro ao cadastrar."

    return render_template('cadastrar.html')

@app.route('/cadastros', methods=['GET', 'POST'])
def cadastros():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome_busca = request.form['nome_busca']
        cadastros = Cadastro.query.filter(Cadastro.nome.like(f'%{nome_busca}%')).order_by(Cadastro.data_hora.desc()).all()
    else:
        cadastros = Cadastro.query.order_by(Cadastro.data_hora.desc()).all()

    return render_template('cadastros.html', cadastros=cadastros)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == '12345678':
            session['loggedin'] = True
            return redirect(url_for('cadastros'))
        else:
            return "Usuário ou senha incorretos!"

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    return redirect(url_for('login'))

@app.route('/download')
def download():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cadastros = Cadastro.query.all()

    if not cadastros:
        return "Nenhum cadastro disponível para download."

    data = {
        'Nome': [cadastro.nome for cadastro in cadastros],
        'Telefone': [cadastro.telefone for cadastro in cadastros],
        'Email': [cadastro.email for cadastro in cadastros],
        'Pretensão': [cadastro.pretensao for cadastro in cadastros],
        'Tipo de Imóvel': [cadastro.tipo_imovel for cadastro in cadastros],
        'Quartos': [cadastro.quartos for cadastro in cadastros],
        'Vagas': [cadastro.vagas for cadastro in cadastros],
        'Suítes': [cadastro.suites for cadastro in cadastros],
        'Data e Hora': [cadastro.data_hora.strftime('%d/%m/%Y %H:%M:%S') for cadastro in cadastros]
    }

    df = pd.DataFrame(data)
    file_path = 'cadastros.xlsx'
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    # Garante que a pasta "instance" exista
    if not os.path.exists(os.path.join(app.root_path, 'instance')):
        os.makedirs(os.path.join(app.root_path, 'instance'))

    app.run(debug=True)
