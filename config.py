# Importa o módulo nativo do Python para interagir com o sistema operacional[cite: 31]
import os
# Importa a função específica para ler arquivos ocultos com extensão .env
from dotenv import load_dotenv

# Aciona a função que carrega as variáveis do .env para a memória temporária do sistema
load_dotenv()

# Cria uma estrutura para agrupar e organizar as configurações globais do aplicativo[cite: 31]
class Config:
    # Puxa o valor de MONGO_URI da memória do sistema e o armazena de forma segura nesta classe
    MONGO_URI = os.getenv('MONGO_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')