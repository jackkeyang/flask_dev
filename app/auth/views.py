#coding=utf8
from . import auth
from flask import render_template, request, url_for, redirect, flash, session, g
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Users, Hosts
import app

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    elif request.method == 'POST':
        data = request.form.to_dict()
        user = Users.query.filter_by(username=data.get('username')).first()
        if user.status:
            if user and user.verify_password(data.get('password')):
                login_user(user)
                return redirect(url_for('auth.dashboard'))
            else:
                flash('Username or Password is Error!')
        else:
            flash('%s is Disabled'%data.get('username'))
        return redirect(url_for('auth.login'))

@auth.route('/dashboard')
@login_required
def dashboard():
    users = Users.query.count()
    hosts = Hosts.query.count()
    return render_template('dashboard.html', hosts=hosts, users=users)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))