#coding=utf8
from . import api
from ..models import Users
from flask import g, jsonify, request, url_for
from errors import unauthorized, bad_request
from authentication import auth
from ..models import db
from decorators import role_required, self_required

# 查看用户列表
@api.route('/users')
@auth.login_required
def users():
    page = request.args.get('page', 1, type=int)
    pagination = Users.query.paginate(page, per_page=2, error_out=False)
    users = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.users', page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.users', page=page + 1, _external=True)
    return jsonify({
        'users': [user.to_json() for user in users],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

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