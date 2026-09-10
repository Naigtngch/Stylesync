from functools import wraps
from flask import request, jsonify, current_app
import jwt


def token_required(f):
    @wraps(f)
    def decoreted(*args, **kwards):

        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'message': 'Token Malformado'}), 401

        if not token:
            return jsonify({'error': 'Token não encontrado'}), 401

        try:
            data = jwt.decode(token,
                               current_app.config['SECRET_KEY'],
                               algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        # CORRIGIDO: rede de segurança para qualquer outro erro inesperado
        # (ex: SECRET_KEY ausente/None por falha no .env), evitando um 500 cru.
        except Exception as e:
            return jsonify({'error': f'Falha ao validar token: {str(e)}'}), 500

        return f(data, *args, **kwards)

    return decoreted