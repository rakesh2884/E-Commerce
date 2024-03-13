from flask import Blueprint, request, jsonify
from .model import User
import re
from flask_mail import Message
from app import mail

from jwt import encode, decode
import os
import time
arr=[]
arr1=[]
active_user=[]
app = Blueprint('app', __name__)
from app.model import  User, Product,CartItem
from app.decorators import is_customer,is_retailer

@app.route('/register', methods=['GET', 'POST'])
def register():
        data=request.get_json()
        username = data['username']
        password = data['password']
        email=data['email']
        role = data['role']
        confirm_password=data['confirm_password']
        if len(password) < 8:
            return jsonify({'message':'Make sure your password is at lest 8 letters'}) 
        elif re.search('[0-9]',password) is None:
            return jsonify({'message':'Make sure your password has a number in it'})
        elif re.search('[A-Z]',password) is None: 
            return jsonify({'message':'Make sure your password has a capital letter in it'})
        elif re.search('[^a-zA-Z0-9]',password) is None:
            return jsonify({'message':'Make sure your password has a special character in it'}) 
        elif password!=confirm_password:
            return jsonify({'message':'password not match'})
        else:
            new_user = User(username=username,password=password,email=email, role=role)
            user=User.query.filter_by(username=username).first()
            if not user:
                active_user.append(username)
                new_user.save()
                return jsonify({'message':'user registered successfully'})
            else:
                return jsonify({'message':'user already exist'})
login_attempts={}
@app.route('/login', methods=['GET', 'POST'])
def login():
        data=request.get_json()
        username = data['username']
        password = data['password']
        email=data['email']
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'message': 'User does not exist'}), 400
        elif user.password != password:
            if username in login_attempts:
                login_attempts[username] += 1
            else:
                login_attempts[username] = 1

            if login_attempts[username] >= 3:
                link = encode({"username":username,"email": email,"action": "deactivate", "timestamp": int(time.time())}, os.getenv('JWT_SECRET_KEY'))
                activation_link = f"http://127.0.0.1:5000/deactivate?link={link}"
                msg = Message(subject='Unauthorized Access', sender=os.getenv('MAIL_USERNAME'), recipients=[email])
                msg.body = "Hey "+ username + " Your account is temporarily locked due to multiple login attempts. Click the link to deactivate your account:" + activation_link
                mail.send(msg)
                return jsonify({'message': 'Last attempt failed (unauthorized access), deactivation link sent to your email'}), 400
            else:
                return jsonify({'message': 'Incorrect password, try again'}), 400
        elif username not in active_user:
            return jsonify({'message': 'User is not activated'}), 400
        
        else:
            token = encode({"email": email,"action": "login", "timestamp": int(time.time())}, os.getenv('JWT_SECRET_KEY'))
            return jsonify({'message': 'Login successful','token': token}), 400
@app.route('/deactivate', methods=['GET'])
def deactivate():
    link = request.args.get('link')
    if link in arr1:
        User.is_valid=True
    else:
        User.is_valid=False
        arr1.append(link)
    if link and User.is_valid!=True:
            decoded_link = decode(link, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
            email = decoded_link.get('email')
            username=decoded_link.get('username')
            User.is_valid=True
            user = User.query.filter_by(username=username).first()
            if user:
                active_user.remove(username)
                return jsonify({'message':'Account deactivated successfully'})
            else:
                return jsonify({'message': 'User does not exist'}), 400
    else:
        return jsonify({'message':'Link is not valid'})

@app.route('/get_activate', methods=['POST','GET'])
def get_activate():
    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data['email']
    user = User.query.filter_by(username=username,password=password).first()
    if user:
        if user.username in active_user:
            return jsonify({'message': 'User already activated'}), 400
        else:
            link = encode({"username":username,"email": email,"password":password,"action": "activate", "timestamp": int(time.time())}, os.getenv('JWT_SECRET_KEY'))
            activation_link = f"http://127.0.0.1:5000/activate?link={link}"
            msg = Message(subject='Activate your Account', sender=os.getenv('MAIL_USERNAME'), recipients=[email])
            msg.body = "Hey,"+ username + "To activate your account. Click the link : " + activation_link
            mail.send(msg)
            return jsonify({'message': 'activation link sent to your email'}), 400
    else:
        return jsonify({'message':'user not exist'})
        

@app.route('/activate', methods=['GET'])
def activate():
    link = request.args.get('link')
    if link in arr:
        User.is_valid=False
    else:
        User.is_valid=True
        arr.append(link)
    if link and User.is_valid!=False:
        decoded_link = decode(link, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
        email = decoded_link.get('email')
        username=decoded_link.get('username')
        password=decoded_link.get('password')
        User.is_valid=False
        user = User.query.filter_by(email=email,password=password).first()
        if user :
            if user:
                active_user.append(username)
                return jsonify({'message': 'Account activated successfully'}), 200
        else:
            return jsonify({'message': 'User does not exist'}), 400
    else:
        return jsonify({'message': 'link is not valid'}), 400


@app.route('/add_product',methods=['GET','POST'])
@is_retailer
def add_product():
    data=request.get_json()
    username=data['username']
    password=data['username']
    user = User.query.filter_by(username=username).first()
    if user and user.password!=password:
        user_id=data['user_id']
        product_name=data['product_name']
        product_price=data['product_price']
        new_product=Product(product_name=product_name,product_price=product_price,user_id=user_id)
        product=Product.query.filter_by(product_name=product_name).first()
        if product:
            return jsonify({'message':'product alraedy exist'})
        else:
            new_product.assign()
            return jsonify({'message':'product added successfully'})
    else:
         return jsonify({'message':'Invalid user'})
    
@app.route('/add_to_cart',methods=['GET','POST'])
@is_customer
def add_to_cart():
    data=request.get_json()
    product_id=data['product_id']
    quantity=data['quantity']
    user_id=data['user_id']
    cart_item = CartItem(user_id=user_id,product_id=product_id, quantity=quantity)
    cart=CartItem.query.filter_by()
    cart_item.add()
    return jsonify({'message': 'Item added to cart successfully'}), 201
@app.route('/check_out',methods=['GET','POST'])
def check_out():
    data=request.get_json()
    product_id=data['product_id']
    user_id=data['user_id']
    email=data['email']
    quantity=data['quantity']
    Address=data['Address']
    PhoneNo=data['PhoneNo']
    cart=CartItem.query.filter_by(user_id=user_id).first()
    if cart:
        cart.remove()
        return jsonify({'message':'Your Order Placed Successfully and Your order is will delieverd to your registered address'+Address})
    else:
        return jsonify({'message':'cart is empty'})
