from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import *
import os


db = SQLAlchemy()

def create_app(app_name):
    app = Flask(__name__)
    app.config.from_object(config[app_name])
    db.init_app(app)

    from auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

    from hosts import hosts
    app.register_blueprint(hosts, url_prefix='/host')

    from api_1_0 import api
    app.register_blueprint(api, url_prefix='/api/v1.0')

    return app