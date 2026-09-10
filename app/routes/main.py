from flask import Blueprint, jsonify, request, current_app, render_template, redirect, url_for, flash, session
from app.models.user import LoginPayModel
from pydantic import ValidationError
from app import db
from bson import ObjectId
from app.models.products import *
from app.models.sale import Sale
from app.decorators import token_required
from datetime import datetime, timedelta, timezone
from werkzeug.security import check_password_hash
import jwt
import csv
import os
import io
 
main_mb = Blueprint('main_mb', __name__)
 
# ==========================================
# ROTAS DE FRONTEND (Telas)
# ==========================================
 
@main_mb.route('/')
def index():
    if 'jwt_token' not in session:
        return redirect(url_for('main_mb.login'))
    return redirect(url_for('main_mb.dashboard'))
 
@main_mb.route('/dashboard')
def dashboard():
    if 'jwt_token' not in session:
        return redirect(url_for('main_mb.login'))
    return render_template('dashboard.html', title='Dashboard')
 
# ==========================================
# ROTAS DE AUTENTICAÇÃO
# ==========================================
 
# RF: Nosso sistema deve permite que o úsario se autentique para obter um token
@main_mb.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            raw_data = request.get_json() if request.is_json else request.form.to_dict()
            user_data = LoginPayModel(**raw_data)
        except ValidationError as e:
            if request.is_json:
                return jsonify({'error': e.errors()}), 400
            else:
                flash('Dados inválidos.', 'danger')
                return redirect(url_for('main_mb.login'))
        except Exception as e:
            return jsonify({'error': 'Erro durante a requisição dos dados'}), 500
 
        # CORRIGIDO: credenciais fixas no código trocadas por consulta ao banco
        # com senha hasheada (nunca comparar senha em texto puro).
        # Espera um documento em db.users no formato:
        #   { "username": "admin", "password_hash": "<hash gerado com generate_password_hash>" }
        user = db.users.find_one({'username': user_data.username})
 
        if user and check_password_hash(user['password_hash'], user_data.password):
            token = jwt.encode(
                {
                    "user_id": user_data.username,
                    "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
                },
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
 
            session['jwt_token'] = token
 
            # CORRIGIDO: era jsonify({...}, 200) -> o 200 virava parte do corpo
            # em vez de status code. Agora o status vem como segundo elemento
            # da tupla de retorno do Flask.
            if request.is_json:
                return jsonify({'access_token': token}), 200
            return redirect(url_for('main_mb.dashboard'))
 
        else:
            if request.is_json:
                return jsonify({'message': 'Credenciais inválidas!'}), 401
 
            flash('Usuário ou senha inválidos.', 'danger')
            return redirect(url_for('main_mb.login'))
 
    return render_template('login.html', title='Login')
 
# ==========================================
# ROTAS DE PRODUTOS
# ==========================================
 
# RF: O sistema deve permitir a listagem de todos os produtos
@main_mb.route('/products', methods=['GET'])
def get_products():
    if 'jwt_token' not in session:
        return redirect(url_for('main_mb.login'))
 
    products_cursor = db.products.find({})
    return render_template('products.html', products=products_cursor, title='Produtos')
 
# RF: O sistema deve permitir a criação de novos produtos
@main_mb.route('/products', methods=['POST'])
@token_required
def create_products(token):
    try:
        # CORRIGIDO: antes só aceitava JSON (request.get_json()), o que
        # quebra com TypeError se um form HTML normal submeter os dados.
        raw_data = request.get_json() if request.is_json else request.form.to_dict()
        product = Product(**raw_data)
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400
    except Exception as e:
        return jsonify({'error': 'Erro ao processar os dados do produto'}), 400
 
    # CORRIGIDO: exclui o campo 'id' (None) do dump, senão o Mongo grava um
    # campo extra "id": null no documento em vez de deixar o _id automático.
    result = db.products.insert_one(product.model_dump(exclude={'id'}))
    return jsonify({'message': 'Produto criado com sucesso', 'id': str(result.inserted_id)}), 201
 
# RF: O sistema deve permitir a visualização dos detalhes de um unico produto
@main_mb.route('/product/<string:product_id>', methods=['GET'])
def get_products_by_id(product_id):
    try:
        oid = ObjectId(product_id)
    except Exception as e:
        # CORRIGIDO: faltava status code -> era 400, virava um "sucesso" pro cliente
        return jsonify({'error': f'Erro ao transformar o:{product_id} em ObjectId: {e}'}), 400
 
    product = db.products.find_one({'_id': oid})
 
    if product:
        # CORRIGIDO: nome da classe (era ProductDBMondel, typo)
        product_model = ProductDBModel(**product).model_dump(by_alias=True, exclude_none=True)
        return jsonify(product_model)
    else:
        # CORRIGIDO: faltava status code -> era 404
        return jsonify({'error': f'Produto com id: {product_id} - Não encontrado'}), 404
 
# RF: O sistema deve permitir a atualização de um único produto e produto existente
@main_mb.route('/products/<string:product_id>', methods=['PUT'])
@token_required
def update_product(token, product_id):
    try:
        oid = ObjectId(product_id)
        update_data = UpdateProduct(**request.get_json())
    except ValidationError as e:
        # CORRIGIDO: era e.errors (sem chamar), serializava a referência do
        # método em vez do conteúdo do erro. Também faltava status code.
        return jsonify({'error': e.errors()}), 400
    except Exception as e:
        return jsonify({'error': f'Id inválido ou dados malformados: {e}'}), 400
 
    update_result = db.products.update_one(
        {'_id': oid},
        {'$set': update_data.model_dump(exclude_unset=True)}
    )
 
    if update_result.matched_count == 0:
        return jsonify({'message': 'Produto não encontrado'}), 404
 
    updated_product = db.products.find_one({'_id': oid})
    # CORRIGIDO: nome da classe (era ProductDBMondel)
    return jsonify(ProductDBModel(**updated_product).model_dump(by_alias=True, exclude_none=True))
 
# RF: O sistema deve permitir a deleção de um único produto e de um produto existente
@main_mb.route('/products/<string:product_id>', methods=['DELETE'])
@token_required
def delete_product(token, product_id):
    try:
        oid = ObjectId(product_id)
    except Exception:
        return jsonify({'error': 'Id do produto inválido'}), 400
 
    # CORRIGIDO: variável local não sobrescreve mais o nome da própria função
    delete_result = db.products.delete_one({'_id': oid})
 
    if delete_result.deleted_count == 0:
        return jsonify({'error': 'Produto não encontrado'}), 404
 
    return '', 204
 
# ==========================================
# ROTAS DE VENDAS
# ==========================================
 
@main_mb.route('/sales/upload', methods=['GET'])
def upload_sale_page():
    if 'jwt_token' not in session:
        return redirect(url_for('main_mb.login'))
    return render_template('upload_sales.html', title='Upload de Vendas')
 
# RF: O sistema deve permitir a importação de vendas atraves de um arquivo
@main_mb.route('/sales/upload', methods=['POST'])
@token_required
def upload_sale(token):
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo foi encontrado'}), 400
 
    file = request.files['file']
 
    if file.filename == '':
        # CORRIGIDO: faltava status code
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
 
    # CORRIGIDO: endswith('csv') aceitava nomes como "relatoriocsv" (sem ponto)
    if file and file.filename.endswith('.csv'):
        csv_stream = io.StringIO(file.stream.read().decode('UTF-8'), newline=None)
        csv_reader = csv.DictReader(csv_stream)
 
        sales_to_insert = []
        error = []
 
        for row_num, row in enumerate(csv_reader, 1):
            try:
                sale_data = Sale(**row)
                sales_to_insert.append(sale_data.model_dump(mode='json'))
            except ValidationError as e:
                error.append(f'Linha {row_num} com dados inválidos')
            except Exception:
                error.append(f'Linha {row_num} com erro nos dados')
 
        if sales_to_insert:
            try:
                db.sale.insert_many(sales_to_insert)
            except Exception as e:
                # CORRIGIDO: faltava status code -> era 500
                return jsonify({'error': str(e)}), 500
 
        return jsonify({
            'message': 'Upload realizado com sucesso',
            'vendas importadas': len(sales_to_insert),
            'erros encontrados': error
        }), 200
 
    # CORRIGIDO: extensão inválida devia retornar erro, não uma mensagem genérica de sucesso
    return jsonify({'error': 'Formato de arquivo inválido. Envie um arquivo .csv'}), 400
 
# ==========================================
# OUTRAS ROTAS
# ==========================================
@main_mb.route('/category', methods=['GET'])
def get_category():
    return jsonify({'message': 'Retorna a lista de todas as categorias'})
 
@main_mb.route('/create_category', methods=['POST'])
def create_category():
    return jsonify({'message': 'Cria nova categoria'})