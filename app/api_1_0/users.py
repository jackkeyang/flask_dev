from . import api
from ..models import Users
from flask import g, jsonify, request
from errors import unauthorized
from authentication import auth

@api.route('/user', methods=['GET', 'POST'])
@auth.login_required
def users():
    if request.method == 'GET':
        users = Users.query.all()
        u_list = []
        for u in users:
            u_list.append(u.to_json())
        return jsonify(u_list)
    elif request.method == 'POST':
        data = request.form.to_dict()
        print data
        return ''

@api.route('/user/<int:uid>')
@auth.login_required
def user(uid):
    user = Users.query.filter_by(id=uid).first()
    return jsonify(user.to_json())