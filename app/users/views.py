#coding=utf8
from . import users
from flask import render_template, request, url_for, redirect, flash, session, jsonify
from ..models import Users, db
from flask_login import login_required
import json

@users.route('/userlist')
@login_required
def userlist():
    page = request.args.get('page', 1, type=int)
    pagination = Users.query.paginate(page, per_page=10, error_out=False)
    return render_template('userlist.html', pagination=pagination)

@users.route('/userinfo', methods=['GET', 'POST'])
@login_required
def userinfo():
    if request.method == 'GET':
        uid = request.args.get("uid")
        user = Users.query.filter_by(id=uid).first_or_404()
        return render_template('userinfo.html', user=user)
    else:
        data = request.form.to_dict()
        uid = data.get("id", "")
        if data.get("status") == "1":
            data["status"] = True
        else:
            data["status"] = False
        data["role"] = Users.roles.get(int(data.get("role")))
        user = Users.query.filter_by(id=uid).update(data)
        db.session.commit()
        return json.dumps({'next': url_for("users.userlist")})

@users.route('/useradd', methods=['GET', 'POST'])
@login_required
def useradd():
    if request.method == 'GET':
        return render_template('useradd.html')
    else:
        data = request.form.to_dict()

        if data.get('status') == '1':
            data['status'] = True
        else:
            data['status'] = False

        print data
        user = Users.query.filter_by(username=data.get('username')).first()
        if not user:
            user = Users(**data)
            db.session.add(user)
            db.session.commit()
            return json.dumps({'next': url_for('users.userlist')})
        else:
            flash('%s already exists!'%user.username)
        return json.dumps({'next': url_for('users.useradd')})
        

@users.route('/userstatus', methods=['POST'])
@login_required
def userstatus():
    data = request.form.to_dict()
    id = data.get("id")
    if data.get("status") == "1":
        data["status"] = True
    else:
        data["status"] = False
    Users.query.filter_by(id=id).update(data)
    db.session.commit()
    return json.dumps({'status': data["status"], 'id': id})

@users.route('/changepasswd', methods=['POST'])
@login_required
def changepasswd():
    data = request.form.to_dict()
    user = Users.query.filter_by(id=data.get('id')).first_or_404()
    user.password = data.get('password1')
    db.session.commit()
    return json.dumps({'next': url_for('users.userlist')})

@users.route('/delete', methods=['POST'])
@login_required
def userdelete():
    data = request.form.to_dict()
    user = Users.query.filter_by(id=data.get('id')).first_or_404()
    db.session.delete(user)
    db.session.commit()
    return json.dumps({'next': url_for('users.userlist')})