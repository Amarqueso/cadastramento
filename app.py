from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cadastros.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de dados com novos campos
class Cadastro(db.Model):
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
    pretensao = request.form['pretensao']
    tipo_imovel = request.form['tipo_imovel']
    quartos = int(request.form['quartos'])
    vagas = int(request.form['vagas'])
    suites = int(request.form['suites'])

    # Cria um novo cadastro e salva no banco de dados
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

    return redirect('/')

# Rota para exibir os cadastros com busca por nome e data no formato brasileiro
@app.route('/cadastros', methods=['GET', 'POST'])
def cadastros():
    if request.method == 'POST':
        nome_busca = request.form.get('nome_busca', '')
        # Busca os cadastros que correspondem ao nome
        todos_cadastros = Cadastro.query.filter(Cadastro.nome.ilike(f'%{nome_busca}%')).order_by(Cadastro.data_hora.desc()).all()
    else:
        # Caso não haja busca, retorna todos os cadastros
        todos_cadastros = Cadastro.query.order_by(Cadastro.data_hora.desc()).all()
    
    # Formatar a data no padrão brasileiro
    for cadastro in todos_cadastros:
        cadastro.data_hora = cadastro.data_hora.strftime('%d/%m/%Y %H:%M:%S')
        
    return render_template('cadastros.html', cadastros=todos_cadastros)

if __name__ == '__main__':
    # Cria o banco de dados se ainda não existir
    with app.app_context():
        db.create_all()
    app.run(debug=True)
