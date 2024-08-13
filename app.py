from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = 'chave_secreta'  # Chave secreta para a sessão

# Caminho absoluto para o banco de dados
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "instance/cadastros.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo do banco de dados
class Cadastro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    pretensao = db.Column(db.String(10), nullable=False)
    tipo_imovel = db.Column(db.String(20), nullable=False)
    quartos = db.Column(db.Integer, nullable=False)
    vagas = db.Column(db.Integer, nullable=False)
    suites = db.Column(db.Integer, nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.now, nullable=False)

# Página Inicial (Cadastro)
@app.route('/', methods=['GET', 'POST'])
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

        novo_cadastro = Cadastro(
            nome=nome,
            telefone=telefone,
            email=email,
            pretensao=pretensao,
            tipo_imovel=tipo_imovel,
            quartos=quartos,
            vagas=vagas,
            suites=suites,
            data_hora=datetime.now()
        )

        db.session.add(novo_cadastro)
        db.session.commit()

        flash('Cadastro realizado com sucesso!')
        return redirect(url_for('cadastrar'))

    return render_template('cadastrar.html')

# Página de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == '12345678':
            session['logged_in'] = True
            return redirect(url_for('cadastros'))
        else:
            flash('Credenciais inválidas. Tente novamente.')
    return render_template('login.html')

# Página de Cadastros
@app.route('/cadastros')
def cadastros():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    todos_cadastros = Cadastro.query.order_by(Cadastro.data_hora.desc()).all()
    return render_template('cadastros.html', cadastros=todos_cadastros)

# Botão para sair da sessão
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Botão para exportar cadastros para Excel
@app.route('/exportar')
def exportar():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    cadastros = Cadastro.query.all()
    cadastros_lista = [
        {
            "Nome": cadastro.nome,
            "Telefone": cadastro.telefone,
            "Email": cadastro.email,
            "Pretensão": cadastro.pretensao,
            "Tipo de Imóvel": cadastro.tipo_imovel,
            "Quartos": cadastro.quartos,
            "Vagas": cadastro.vagas,
            "Suítes": cadastro.suites,
            "Data e Hora": cadastro.data_hora
        }
        for cadastro in cadastros
    ]

    df = pd.DataFrame(cadastros_lista)
    caminho_arquivo = os.path.join(base_dir, 'instance/cadastros_exportados.xlsx')
    df.to_excel(caminho_arquivo, index=False)

    return f'Cadastros exportados para {caminho_arquivo} com sucesso!'

if __name__ == '__main__':
    app.run(debug=True)
