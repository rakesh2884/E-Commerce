
from flask import Flask, Request, request,jsonify
from flask_login import login_user



app = Flask(__name__)
app.config['SECRET_KEY'] = 'key for login form'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/store0'

from model import  User, Product
from decorators import is_customer,is_retailer
@app.route('/register', methods=['GET', 'POST'])
def register():
        data=request.get_json()
        username = data['username']
        password = data['password']
        role = data['role']
        new_user = User(username=username,password=password, role=role)
        user=User.query.filter_by(username=username).first()
        if not user:
            new_user.save()
            return jsonify({'message':'user registered successfully'})
        else:
            return jsonify({'message':'User already exists'})
@app.route('/login', methods=['GET', 'POST'])
def login():
        data=request.get_json()
        username = data['username']
        password = data['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password==password:
            return jsonify({'message':'login successful'})
        else:
            return jsonify({'message':'invalid credentials'})
@app.route('/add_product',methods=['GET','POST'])
@is_retailer
def add_product():
    data=request.get_json()
    username=data['username']
    password=data['username']
    user = User.query.filter_by(username=username,password=password).first()
    if not user:
        product_name=data['product_name']
        product_price=data['product_price']
        new_product=Product(product_name=product_name,product_price=product_price)
        product=Product.query.filter_by(product_name=product_name).first()
        if product:
            return jsonify({'message':'product alraedy exist'})
        else:
            new_product.assign()
            return jsonify({'message':'product added successfully'})
    else:
         return jsonify({'message':'Invalid user'})
if __name__ == '__main__':
    app.run(debug=True)
