# Importa a fábrica principal do framework para criar o servidor web
from flask import Flask

# Importa o "carteiro" do PyMongo que fará as viagens até o banco de dados
from pymongo import MongoClient

# Cria uma variável global vazia para guardar o acesso ao banco de dados mais tarde
db = None

# Cria a função padrão (Application Factory) que monta, configura e devolve o aplicativo pronto
def create_app():
    # Inicializa o aplicativo Flask definindo este arquivo como a base do projeto
    app = Flask(__name__)
    # Puxa o endereço secreto do MongoDB do arquivo config.py e guarda na memória do Flask
    app.config.from_object('config.Config')
    # Avisa a função para usar aquela variável 'db' que foi criada lá em cima, em vez de criar uma nova
    global db

    # Inicia a rede de segurança: tenta conectar ao banco sem deixar o site cair se algo der errado
    try:
        # Usa o endereço salvo no Flask para criar a linha telefônica com o servidor do MongoDB
        client = MongoClient(app.config['MONGO_URI'])
        # Abre a porta da sala do banco de dados específico (Stylesync) e guarda a chave na variável 'db'
        db = client.get_default_database()
    # Se a conexão falhar (ex: internet caiu), captura o motivo do erro
    except Exception as e:
        # Mostra o erro no terminal do desenvolvedor para facilitar o conserto
        print(f'Erro ao realizar a conexão com o banco de dados: {e}')

    # Importa a sua "planta baixa" (Blueprint) contendo todas as rotas de usuários e produtos
    from .routes.main import main_mb
    # Encaixa o Blueprint no aplicativo principal, ativando as rotas oficialmente
    app.register_blueprint(main_mb)

    # Devolve o aplicativo totalmente montado, conectado ao banco e com as rotas prontas
    return app