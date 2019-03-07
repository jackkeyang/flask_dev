from flask import Blueprint

hosts = Blueprint('hosts', __name__)

from . import views