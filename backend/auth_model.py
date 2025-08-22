from flask import Blueprint, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, get_jwt, unset_jwt_cookies
)
from model import db, User
import uuid

auth_bp = Blueprint('auth', __name__)
CORS(auth_bp) 
# Simulated blacklist (for real apps, use Redis or DB)
jwt_blacklist = set()


@auth_bp.route('/createAccount', methods=['POST'])
def createAccount():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    

    if not all([email, password]):
        return jsonify({'error': 'Missing fields'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    new_user = User(
        id=str(uuid.uuid4()),
        email=email,
        
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    # Auto-login after account creation
    access_token = create_access_token(identity=new_user.id)
    return jsonify({'access_token': access_token, 'message': 'Account created'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200


@auth_bp.route('/getCurrentUser', methods=['GET'])
@jwt_required()
def getCurrentUser():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    jwt_blacklist.add(jti)

    response = jsonify({"message": "Logged out successfully"})
    unset_jwt_cookies(response)
    return response, 200


@auth_bp.route('/updateAccount', methods=['POST'])
@jwt_required()
def updateAccount():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.set_password(data['password'])

    db.session.commit()
    return jsonify({'message': 'Account updated successfully'}), 200
