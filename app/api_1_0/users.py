#coding=utf8
from . import api
from ..models import Users
from flask import g, jsonify, request
from errors import unauthorized, bad_request
from authentication import auth
from ..models import db
from decorators import role_required, self_required

# 查看用户列表
@api.route('/users')
@auth.login_required
def users():
    users = Users.query.all()
    u_list = []
    for u in users:
        u_list.append(u.to_json())
    return jsonify({'code': 200, 'message': u_list})

# 添加用户
@api.route('/users', methods=['POST'])
@auth.login_required
@role_required('ADMIN')
def new_users():
    data = request.form.to_dict()
    user = Users(**data)
    db.session.add(user)
    db.session.commit()
    return jsonify({'code': 200, 'message': '用户添加成功'})

# 查看和修改单个用户信息, 非管理员用户只能查看和更改自己的信息
@api.route('/users/<int:uid>', methods=['GET', 'PUT'])
@auth.login_required
@self_required
def user(uid):
    if request.method == 'GET':
        user = Users.query.filter_by(id=uid).first_or_404()
        return jsonify({'code': 200, 'message': user.to_json()})
    elif request.method == 'PUT':
        data = request.form.to_dict()
        print data
        #uid = data.get('id', None)
        # Users.query.filter_by(id=uid).update(**data)
        user = Users.query.filter_by(id=uid).first_or_404()
        user.username = data.get('username', user.username)
        user.name_cn = data.get('name_cn', user.name_cn)
        user.role = data.get('role', user.role)
        user.email = data.get('email', user.email)
        user.phone = data.get('phone', user.phone)
        user.group = data.get('group', None)
        db.session.commit()
        return jsonify({'code': 200, 'message': '用户修改成功'})

# 删除用户
@api.route('/users/<int:uid>', methods=['DELETE'])
@auth.login_required
@role_required('ADMIN')
def del_users(uid):
    user = Users.query.filter_by(id=uid).first_or_404()
    if user == g.current_user:
        return bad_request('Did Not Delete Yourself')
    db.session.delete(user)
    db.session.commit()
    return jsonify({'code': 200, 'message': 'Delete User Success'})