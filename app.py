from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configuração do banco de dados SQLite para a pasta 'instance'
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
    try:
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
        return redirect('/cadastros')
    except Exception as e:
        return f'Erro ao cadastrar: {e}'

@app.route('/cadastros', methods=['GET', 'POST'])
def cadastros():
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

if __name__ == '__main__':
    # Cria a pasta instance se não existir
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
    
    # Imprime o caminho do banco de dados para verificação
    print("Caminho do banco de dados:", os.path.join(app.instance_path, 'cadastros.db'))

    with app.app_context():
        try:
            db.create_all()  # Cria as tabelas no banco de dados
            print("Banco de dados e tabelas criados com sucesso.")  # Mensagem de depuração
        except Exception as e:
            print(f'Erro ao criar o banco de dados e tabelas: {e}')
    app.run(debug=True)
