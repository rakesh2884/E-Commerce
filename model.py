from __main__ import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy(app)

class User( db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False) 

    def save(self):
        db.session.add(self)
        db.session.commit()
    def remove(self):
        db.session.delete(self)
        db.session.commit()
with app.app_context():
    db.create_all()
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    def assign(self):
        db.session.add(self)
        db.session.commit()
    def remove(self):
        db.session.delete(self)
        db.session.commit()
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    def add(self):
        db.session.add(self)
        db.session.commit()
    def remove(self):
        db.session.delete(self)
        db.session.commit()
with app.app_context():
    db.create_all()