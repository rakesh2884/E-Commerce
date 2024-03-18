from flask import Blueprint, request, jsonify
from .model import User
import re
from flask import render_template
from flask_mail import Message
from app import mail
from flask import session
from jwt import encode, decode
import os
import time
arr=[]
arr1=[]
active_user=[]
log_in={}
app = Blueprint('app', __name__)
from app.model import  User, Product,CartItem, Notification
from app.decorators import is_customer,is_retailer,require_api_token

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'confirm_password' in request.form and 'role' in request.form:
        username = request.form['username']
        password = request.form['password']
        confirm_password=request.form['confirm_password']
        email=request.form['email']
        role=request.form['role']
        
        existing_user= User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'message':'Account already exists !'})
        if len(password) < 8:
            return jsonify({'message':'Make sure password is at least of 8 character'})
        elif re.search('[0-9]',password) is None:
            return jsonify({'message':'Make sure your password has a number in it'})
        elif re.search('[A-Z]',password) is None: 
            return jsonify({'message':'Make sure your password has a capital letter in it'})
        elif re.search('[^a-zA-Z0-9]',password) is None:
            return jsonify({'message':'Make sure your password has a spexial character in it'})
        elif password!=confirm_password:
            return jsonify({'message':'Password not match'})
        else:
            user = User(username=username,password=password,email=email,role=role)
            active_user.append(username)
            user.save()
            return jsonify({'message':'registered successful'}),401
    return render_template('register.html')


login_attempts={}
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email=request.form['email']
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
            token=encode({"username":username,"email": email,"password":password,"action": "activate", "timestamp": int(time.time())}, os.getenv('JWT_SECRET_KEY'))
            log_in['token']=token
            return jsonify({'mssg':'Login successful'})   
    return render_template('login.html')
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
@app.route('/products',methods=['GET'])
def products():
    return render_template('product.html') 


@app.route('/add_to_cart',methods=['GET','POST'])
@is_customer
def add_to_cart():
    data=request.get_json()
    product_id=data['product_id']
    quantity=data['quantity']
    user_id=data['user_id']
    cart_item = CartItem(user_id=user_id,product_id=product_id, quantity=quantity)
    cart_item.add()
    return jsonify({'message': 'Item added to cart successfully'}), 201


@app.route('/my_cart',methods=['GET'])
def my_cart():
    return render_template('cart.html') 

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
        product = Product.query.filter_by(id=product_id).first()
        if product:
            retailer = User.query.filter_by(id=user_id).first()
            if retailer:
                msg = Message(subject='New Order', sender=os.getenv('MAIL_USERNAME'), recipients=[retailer.email])
                msg.body = f"Dear {retailer.username}, you have a new order for the product: {product.product_name}."
                mail.send(msg)
                notifi=f"Dear {retailer.username}, you have a new order for the product: {product.product_name}."
                new_notification=Notification(user_id=user_id,product_id=product_id,Notifications=notifi) 
                new_notification.add()       
            return jsonify({'message':'Your Order Placed Successfully and Your order is will delieverd to your registered address'+Address})
        
    else:
        return jsonify({'message':'cart is empty'})
        

@app.route('/notifications', methods=['GET'])
def get_notifications():
    n=[]
    if 'token' in log_in:
        token=log_in['token']
        decoded_token = decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
        username=decoded_token.get('username')
        user=User.query.filter_by(username=username).first()
        notification=Notification.query.filter_by(user_id=user.id).all()
        for notify in notification:
            n.append(notify.Notifications)
        return n
    else:
        return "not login"