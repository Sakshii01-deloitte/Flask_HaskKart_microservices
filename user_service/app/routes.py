from functools import wraps
from urllib import response
from flask import Flask, request, jsonify, make_response, Response
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
from app import app, db 
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
import config
import requests


PRODUCT_SERVICE_URL = 'http://127.0.0.1:5001/product/'


@app.before_first_request
def create_tables():
    db.create_all()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            app.logger.error('Token is missing!')
            return jsonify({'message' : 'Token is missing!'}), 401

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id=data['id']).first()
            print(current_user.username)
        except:
            app.logger.error('Token is invalid!')
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


#Fetch all the user if and only if the current user is admin
@app.route('/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    app.logger.info("get_all_users")
    if  current_user.type != "admin":
        app.logger.error("cannot perform the action")
        return jsonify({'message' : 'Cant perfom action'}), 401
    
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['username'] = user.username
        user_data['name'] = user.name
        user_data['email'] = user.email
        user_data['password'] = user.password
        user_data['type'] = user.type
        output.append(user_data)
        
    response = jsonify({'users': output})
    return response

#create admin
@app.route('/admin/signup',methods=['POST'])
def create_admin():
    app.logger.info("admin CREATING")
    data = request.get_json()
    
    print("add user start")
    hashed_password = generate_password_hash(data['password'],method='sha256')
    
    new_user = User(username = data['username'],email = data['email'],name = data['name'],password = hashed_password,type = "admin")
    
    db.session.add(new_user)
    print("add user")
    db.session.commit()
    print("add user comit")
    app.logger.info("admin Ceation complete")
    response = jsonify({'message':'New admin created successfully'}),201
    return response

# Customer Signup
@app.route('/customer/signup',methods = ['POST'])
def signup_customer():
    app.logger.info("customer Signup start")
    data = request.get_json()
    
    # print("signup customer initiated")
    # if(User.query.filter(username = data['username']).first()):
    #     response = jsonify({'message':'Username already exist'}),401
    #     print("first response",response)
    #     return response
    
    # if(User.query.filter(email = data['email']).first()):
    #     response = jsonify({'message':'email already exist'}),401
    #     print("sencond response",response)
    #     return response
    
    hashed_password = generate_password_hash(data['password'],method='sha256')
    new_user = User(username = data['username'],email = data['email'],name = data['name'],password = hashed_password, type = "user")
    db.session.add(new_user)
    db.session.commit()
    app.logger.info("Customer Ceation complete")
    response = jsonify({'message':'New Customer created successfully'}),201
    return response
    
    
#login for customer and admin
@app.route('/login', methods=['POST'])
def login():
    app.logger.info('login initiated')
    print('initiated')
    auth = request.get_json()
    username1 = auth['username']
    print("user name",username1)
    password1 = auth['password']
    print("user name pw",password1)
   
    
    if not username1 or  not password1:
        app.logger.error('Could not verify, Incorrect username or password')
        response = make_response('Could not verify, Incorrect username or password', 401,{'WWW-Authenticate':'Basic realm="Login Required'})
        return response
    user = User.query.filter_by(username=username1).first()
    print("filtered user",user)
    
    if not user:
        app.logger.error('Could not find user')
        response = make_response('Could not find user', 401,{'WWW-Authenticate':'Basic realm="Login Required'})
        return response
    
    if check_password_hash(user.password, password1):
        token = jwt.encode({'id':user.id,'type':user.type,'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=120)},
        app.config['SECRET_KEY'])
        
        response = jsonify({'token':token.decode('UTF-8')})
        print("total response",response)
        return response
    response = {"msg":"Incorrect password"}
    print(response)
    return response


#get detail of logged in user
@app.route('/currentUser/info', methods=['GET'])
@token_required
def get_user(current_user):
    print("currentUser",current_user)
    app.logger.info('get_user')
    user_data = {}
    user_data['id'] = current_user.id
    user_data['username'] = current_user.username
    user_data['email'] = current_user.email
    user_data['name'] = current_user.name
    user_data['type']= current_user.type
    response = jsonify(user_data)
    return response


# adding delete user feature
@app.route('/user/deleteUser/<id>', methods=['DELETE'])
@token_required
def delete_user(current_user,id):
    app.logger.info('delete_user')
    if  current_user.type != "admin":
        app.logger.info("Action can't be performed,User is not admin")
        return jsonify({'message': "Action can't be performed,User is not admin"}),401
    user = User.query.filter_by(id=id).first()
    if not user:
        app.logger.info("No user found")
        return jsonify({'message': "No user found"}),404
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': "User is deleted Successfully"}),200



#admin can add new product
@app.route('/addproduct', methods=['POST'])
@token_required
def add_product(current_user):
    app.logger.info("Add Products")
    try:
        if current_user.type == 'admin':
            res = requests.post('http://127.0.0.1:5001/product' + str(current_user.id),json=request.get_json())
            return res.json()
        else:
            return jsonify({'message': "cant perform action"}),403
    except :
        return jsonify({'message': "cant perform action"}),500
    
    
    
#user can fetch product by id
@app.route('/product/<id>', methods=['GET'])
@token_required
def get_product(current_user, id):
    app.logger.info('get product')
    res = requests.get(PRODUCT_SERVICE_URL+ id)
    return res.json(), res.status_code



#Fetch all the products
@app.route('/products', methods=['GET'])
@token_required
def get_all_products(current_user):
    res = requests.get('http://127.0.0.1:5001/products')
    return res.json(), res.status_code




 
