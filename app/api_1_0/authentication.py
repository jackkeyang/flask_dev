from flask import g, jsonify
from ..models import Users
from . import api
from errors import unauthorized, forbidden
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    user = Users.verify_auth_token(username_or_token)
    use_token = True
    if not user:
        user = Users.query.filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
        use_token = False
    g.current_user = user
    g.token_used = use_token
    return True
    # if username_or_token is None:
    #     return False
    # if password is None:
    #     g.current_user = Users.verify_auth_token(username_or_token)
    #     g.token_used = True
    #     return g.current_user is not None
    # user = Users.query.filter_by(username=username_or_token).first()
    # if not user:
    #     return False
    # g.current_user = user
    # g.token_used = False
    # return user.verify_password(password)

# @api.before_request
# @auth.login_required
# def before_request():
#     # if not g.current_user.is_anonymous and not g.current_user.confiremd:
#     if not g.current_user.is_anonymous or g.token_used:
#         return forbidden('Unconfirmed account')

@api.route('/tokens', methods=['POST'])
@auth.login_required
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized("Invalid credentials")
    return jsonify({'token': g.current_user.getnerate_reset_token(expiration=3600), 'expiration': 3600})

@api.route('/test')
@auth.login_required
def test():
    print 'test'
    return 'okaaaaaaaa'