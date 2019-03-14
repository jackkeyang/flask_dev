from functools import wraps
from flask import g, request
from .errors import forbidden

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorator_function(*args, **kwargs):
            if g.current_user.role != role:
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)
        return decorator_function
    return decorator

def self_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        uid = int(request.path.split('/')[-1])
        if g.current_user.role != 'ADMIN':
            if g.current_user.id != uid:
                return forbidden('Insufficient permissions')
        return f(*args, **kwargs)    
    return decorator