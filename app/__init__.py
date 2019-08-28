from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from flask_login import LoginManager
from config import *
import os


db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(app_name):
    app = Flask(__name__)
    app.config.from_object(config[app_name])
    app.config.from_object('app.schduler')
    db.init_app(app)

    # scheduler = APScheduler()
    # scheduler.init_app(app)
    # scheduler.start()

    login_manager.init_app(app)

    from auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

    from users import users
    app.register_blueprint(users, url_prefix='/users')

    from hosts import hosts
    app.register_blueprint(hosts, url_prefix='/hosts')

    from api_1_0 import api
    app.register_blueprint(api, url_prefix='/api/v1.0')

    return app
