"""
Script único para criar o usuário admin inicial com senha hasheada.
Rode uma vez (python seed_admin.py) depois de configurar o .env.

Necessário porque o login deixou de aceitar credenciais fixas no código
('admin' / '12345') e passou a consultar a coleção db.users.
"""
import os
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv('MONGO_URI'))
db = client.get_default_database()

username = 'admin'
password = 'Magiku'  # troque por uma senha forte antes de rodar

existing = db.users.find_one({'username': username})
if existing:
    print(f'Usuário "{username}" já existe. Nada foi feito.')
else:
    db.users.insert_one({
        'username': username,
        'password_hash': generate_password_hash(password)
    })
    print(f'Usuário "{username}" criado com sucesso.')