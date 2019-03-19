#coding=utf8
from . import auth
from flask import render_template, request, url_for, redirect, flash, session
from flask_login import login_user, logout_user
from ..models import Users

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    elif request.method == 'POST':
        data = request.form.to_dict()
        user = Users.query.filter_by(username=data.get('username')).first()
        if user and user.verify_password(data.get('password')):
            login_user(user)
            session['username'] = user.username
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Username or Password is Error!')
            return redirect(url_for('auth.login'))

@auth.route('/dashboard')
def dashboard():
    data = {
        'username': session.get('username', None)
    }
    return render_template('dashboard.html', **data)