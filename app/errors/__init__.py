from flask import Blueprint

bp = Blueprint('erros',__name__)

from app.errors import handlers