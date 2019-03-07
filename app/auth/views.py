from . import auth

@auth.route('/aaa')
def index():
    return '<p>aaa</p>'