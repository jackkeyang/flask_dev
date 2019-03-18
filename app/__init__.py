from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from config import *
import os


db = SQLAlchemy()

def create_app(app_name):
    app = Flask(__name__)
    app.config.from_object(config[app_name])
    app.config.from_object('app.schduler')
    db.init_app(app)

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    from auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

    from hosts import hosts
    app.register_blueprint(hosts, url_prefix='/host')

    from api_1_0 import api
    app.register_blueprint(api, url_prefix='/api/v1.0')

    return app
