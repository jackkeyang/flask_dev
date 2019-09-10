from flask import Blueprint

assets = Blueprint('asset', __name__)

from . import views