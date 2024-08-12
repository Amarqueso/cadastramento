from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cadastro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definição do modelo para armazenar os cadastros
class Cadastro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Cadastro {self.nome}>'

# Rota para a página inicial e processamento do formulário
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        email = request.form['email']
        
        # Cria um novo registro de cadastro
        novo_cadastro = Cadastro(nome=nome, telefone=telefone, email=email)

        try:
            db.session.add(novo_cadastro)
            db.session.commit()
            return redirect(url_for('index'))
        except:
            return 'Houve um problema ao salvar seu cadastro.'

    return render_template('index.html')

@app.route('/cadastros')
def cadastros():
    # Busca todos os cadastros no banco de dados
    todos_cadastros = Cadastro.query.order_by(Cadastro.data_hora.desc()).all()
    return render_template('cadastros.html', cadastros=todos_cadastros)





# Inicializa o banco de dados
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
