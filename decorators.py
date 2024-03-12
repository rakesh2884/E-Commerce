from functools import wraps
from flask import request, jsonify
from model import User
def is_retailer(f):
    @wraps(f)
    def inner(*args, **kwargs):
        data=request.get_json()
        username=data['username']
        password=data['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password==password:
            if user.role=="retailer":
                return f(*args, **kwargs)
            else:
                return jsonify({'message':'no access'}),401
        else:
            return jsonify({'message':'Invalid User'}),401
    return inner
def is_customer(f):
    @wraps(f)
    def inner(*args, **kwargs):
        data=request.get_json()
        username=data['username']
        password=data['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password==password:
            if user.role=="customer":
                return f(*args, **kwargs)
            else:
                return jsonify({'message':'no access'}),401
        else:
            return jsonify({'message':'Invalid User'}),401
    return inner