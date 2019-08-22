from flask_login import current_user
from functools import wraps
from errors import forbidden

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorator_function(*args, **kwargs):
            if current_user.role != role:
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)
        return decorator_function
    return decorator