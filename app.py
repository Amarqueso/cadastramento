from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cadastros.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de dados
class Cadastro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Cadastro {self.nome}>'

# Rota principal para exibir o formulário de cadastro
@app.route('/')
def index():
    return render_template('index.html')

# Rota para processar o cadastro
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form['nome']
    telefone = request.form['telefone']
    email = request.form['email']

    # Cria um novo cadastro e salva no banco de dados
    novo_cadastro = Cadastro(nome=nome, telefone=telefone, email=email)
    db.session.add(novo_cadastro)
    db.session.commit()

    return redirect('/')

# Rota para exibir os cadastros
@app.route('/cadastros')
def cadastros():
    # Busca todos os cadastros no banco de dados, ordenados por data/hora
    todos_cadastros = Cadastro.query.order_by(Cadastro.data_hora.desc()).all()
    return render_template('cadastros.html', cadastros=todos_cadastros)

if __name__ == '__main__':
    # Cria o banco de dados se ainda não existir
    db.create_all()
    app.run(debug=True)
