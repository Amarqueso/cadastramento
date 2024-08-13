from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import openpyxl

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/cadastro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o banco de dados
db = SQLAlchemy(app)

# Modelo do banco de dados
class Cadastro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    pretensao = db.Column(db.String(20))
    tipo_imovel = db.Column(db.String(50))
    quartos = db.Column(db.Integer)
    vagas = db.Column(db.Integer)
    suites = db.Column(db.Integer)
    data_hora = db.Column(db.DateTime, default=datetime.now)

# Página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '12345678':
            session['logged_in'] = True
            return redirect(url_for('cadastros'))
        else:
            error = 'Usuário ou senha inválidos'
    return render_template('login.html', error=error)

# Página de logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Página de cadastramento
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        email = request.form['email']
        pretensao = request.form['pretensao']
        tipo_imovel = request.form['tipo_imovel']
        quartos = request.form['quartos']
        vagas = request.form['vagas']
        suites = request.form['suites']
        novo_cadastro = Cadastro(nome=nome, telefone=telefone, email=email, pretensao=pretensao, tipo_imovel=tipo_imovel, quartos=quartos, vagas=vagas, suites=suites)
        db.session.add(novo_cadastro)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('index.html')

# Página de visualização de cadastros
@app.route('/cadastros')
def cadastros():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    cadastros = Cadastro.query.order_by(Cadastro.data_hora.desc()).all()
    return render_template('cadastros.html', cadastros=cadastros)

# Função para baixar cadastros como Excel
@app.route('/download_excel')
def download_excel():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Criar um novo arquivo Excel
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Cadastros'

    # Cabeçalhos
    sheet.append(['Nome', 'Telefone', 'Email', 'Pretensão', 'Tipo de Imóvel', 'Quartos', 'Vagas', 'Suítes', 'Data e Hora'])

    # Dados
    cadastros = Cadastro.query.all()
    for cadastro in cadastros:
        sheet.append([cadastro.nome, cadastro.telefone, cadastro.email, cadastro.pretensao, cadastro.tipo_imovel, cadastro.quartos, cadastro.vagas, cadastro.suites, cadastro.data_hora])

    # Salvar o arquivo temporariamente
    file_path = 'cadastros.xlsx'
    workbook.save(file_path)

    # Enviar o arquivo para o usuário
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
