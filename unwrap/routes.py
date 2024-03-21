import os
import secrets
from flask import render_template, url_for, flash, redirect, request, jsonify
from unwrap import app, db, bcrypt
from unwrap.forms import RegistrationForm, LoginForm, UpdateAccountForm, AddProductForm
from flask_paginate import Pagination, get_page_args
from unwrap.models import User, Products, Cart
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import func, update
from wtforms import Form
from werkzeug.utils import secure_filename
from PIL import Image
def getLoginDetails():
    if current_user.is_authenticated:
        noOfItems = Cart.query.filter_by(buyer=current_user).count()
    else:
        noOfItems = 0
    return noOfItems


@app.route("/")
@app.route("/home")
def home():
    noOfItems = getLoginDetails()
    return render_template('home.html', noOfItems=noOfItems)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(lastname=form.lastname.data,firstname=form.firstname.data,email=form.email.data, password=hashed_password,role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.lastname = form.lastname.data
        current_user.firstname = form.firstname.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.lastname.data = current_user.lastname
        form.firstname.data = current_user.firstname
        form.email.data = current_user.email
    return render_template('account.html', title='Account',
                           form=form)


def get_products(offset=0, per_page=10):
    products = Products.query.all()
    return products[offset: offset + per_page]

@app.route("/select_products", methods=['GET', 'POST'])
def select_products():
    products = Products.query.all()
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    total=len(products)
    pagination_products = get_products(offset=offset,per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page,total=total,
                            css_framework='bootstrap4')
    return render_template('select_products.html',
                           products=pagination_products,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           )


@app.route("/addToCart/<int:product_id>")
@login_required
def addToCart(product_id):
    row = Cart.query.filter_by(product_id=product_id, buyer=current_user).first()
    if row:
        row.quantity += 1
        db.session.commit()
        flash('This item is already in your cart, 1 quantity added!', 'success')
    else:
        user = User.query.get(current_user.id)
        user.add_to_cart(product_id)
    return redirect(url_for('select_products'))


@app.route('/add_product',methods=['GET','POST'])
def add_product():
    
    name=request.form.get("name")
    price=request.form.get("price")
    description=request.form.get("description")
    image=request.files["image"]
    i=os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    return i
@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    noOfItems = getLoginDetails()
    cart = Products.query.join(Cart).add_columns(Cart.quantity, Products.price, Products.name, Products.id).filter_by(id=Products.id).all()
    subtotal = 0
    for item in cart:
        subtotal+=int(item.price)*int(item.quantity)

    if request.method == "POST":
        qty = request.form.get("qty")
        idpd = request.form.get("idpd")
        cartitem = Cart.query.filter_by(product_id=idpd).first()
        cartitem.quantity = qty
        db.session.commit()
        cart = Products.query.join(Cart).add_columns(Cart.quantity, Products.price, Products.name, Products.id).filter_by(id=Products.id).all()
        subtotal = 0
        for item in cart:
            subtotal+=int(item.price)*int(item.quantity)
    return render_template('cart.html', cart=cart, noOfItems=noOfItems, subtotal=subtotal)

@app.route("/removeFromCart/<int:product_id>")
@login_required
def removeFromCart(product_id):
    item_to_remove = Cart.query.filter_by(product_id=product_id, buyer=current_user).first()
    db.session.delete(item_to_remove)
    db.session.commit()
    flash('Your item has been removed from your cart!', 'success')
    return redirect(url_for('cart'))