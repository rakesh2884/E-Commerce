from functools import wraps
from flask import request, jsonify
from app.model import User
import os
import jwt
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

def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       token = None
       if 'x-access-tokens' in request.headers:
           token = request.headers['x-access-tokens']
 
       if not token:
           return jsonify({'message': 'a valid token is missing'})
       try:
           data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
           current_user = User.query.filter_by(id=id).first()
       except:
           return jsonify({'message': 'token is invalid'})
 
       return f(current_user, *args, **kwargs)
   return decorator