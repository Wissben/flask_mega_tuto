import os

from dotenv import load_dotenv

APP_ROOT = os.path.dirname(os.path.abspath(
    __file__))  # refers to application_top
APP_BASE_DIR = os.path.abspath(os.path.dirname(__file__))
APP_DATA_BASE_DIR = os.path.join(APP_ROOT, 'app', 'database')
APP_STATIC = os.path.join(APP_ROOT, 'app', 'static')


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'the_north_remembers'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///' + os.path.join(APP_DATA_BASE_DIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['wissam.benhaddad.pro@gmail.com']

    LANGUAGES = ['en', 'es']

    MAX_POST_PER_PAGE = 3

    AUTHORIZED_EXTENSIONS = ['wav', 'mp3']
    UPLOAD_FOLDER = os.path.join(APP_STATIC)

    ELASTICSEARCH_URL = 'http://localhost:9200'

    TF_SERVING_URL = 'http://localhost:8051/v1/models/test_model'
