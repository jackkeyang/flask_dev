#coding=utf8
from . import users
from flask import render_template, request, url_for, redirect, flash, session
from ..models import Users

@users.route('/userlist')
def userlist():
    data = {
        'username': session.get('username', None)
    }
    return render_template('userlist.html', **data)