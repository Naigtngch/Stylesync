# StyleSync — API de Gestão de Produtos e Vendas

Backend em Flask para gestão de produtos, controle de estoque e importação de vendas via CSV, com autenticação via JWT e front-end simples em HTML/Bootstrap para operação via navegador.

> Projeto desenvolvido com base no curso de Python/Flask da [Alura](https://www.alura.com.br/), com extensões e correções próprias (validação com Pydantic, autenticação JWT, tratamento de erros, segurança de senha).

## Funcionalidades

- Autenticação de usuários via JWT
- CRUD completo de produtos (criar, listar, detalhar, atualizar, excluir)
- Importação em massa de vendas via upload de arquivo CSV
- Validação rigorosa de dados de entrada com Pydantic
- Modelagem orientada a documentos com MongoDB (PyMongo)
- Rotas protegidas por token, com decorator reutilizável

## Tecnologias

- Python 3
- Flask (Blueprints)
- MongoDB + PyMongo
- Pydantic (validação e serialização)
- PyJWT (autenticação)
- Werkzeug Security (hash de senha)
- Bootstrap 5 (telas HTML)

## Estrutura do projeto

```
app/
├── models/
│   ├── category.py
│   ├── products.py
│   ├── sale.py
│   └── user.py
├── routes/
│   └── main.py
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── products.html
│   ├── add_product.html
│   └── upload_sales.html
├── decorators.py
└── __init__.py
config.py
run.py
seed_admin.py
```

## Como rodar o projeto

### 1. Pré-requisitos
- Python 3.10+
- Uma instância MongoDB (local ou Atlas)

### 2. Clone o repositório
```bash
git clone https://github.com/Naigtngch/Stylesync
cd stylesync
```

### 3. Crie e ative um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 4. Instale as dependências
```bash
pip install -r requirements.txt
```

### 5. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:
```
MONGO_URI=sua_connection_string_do_mongodb
SECRET_KEY=uma_chave_secreta_aleatoria
```

### 6. Crie o usuário administrador inicial
```bash
python seed_admin.py
```
> Edite a senha padrão dentro do script antes de rodar.

### 7. Rode a aplicação
```bash
python run.py
```
A aplicação sobe em `http://localhost:5000`.

## Rotas da API

| Método | Rota | Descrição | Autenticação |
|---|---|---|---|
| POST | `/login` | Autentica e retorna token JWT | Não |
| GET | `/products` | Lista todos os produtos | Sessão |
| POST | `/products` | Cria um novo produto | Token JWT |
| GET | `/product/<id>` | Detalha um produto | Não |
| PUT | `/products/<id>` | Atualiza um produto | Token JWT |
| DELETE | `/products/<id>` | Remove um produto | Token JWT |
| POST | `/sales/upload` | Importa vendas via CSV | Token JWT |

## Próximos passos / melhorias planejadas

- [ ] Implementar CRUD completo de categorias (atualmente stub)
- [ ] Adicionar testes automatizados
- [ ] Endpoint de logout
- [ ] Paginação na listagem de produtos

## Autor

Gianlucas Hikaru Taniguchi Santos — [LinkedIn](#) | [GitHub](#)