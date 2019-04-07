from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from logging.handlers import SMTPHandler,RotatingFileHandler

import logging
import os

#Helper functions :
def setup_mail_logging():
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
                                   mailhost=(app.config['MAIL_SERVER'],app.config['MAIL_PORT']),
                                   fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                                   toaddrs=app.config['ADMINS'],
                                   subject='Errors logs',
                                   credentials=auth, secure=secure
                                   )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


def setup_file_logging():
    if not os.path.exists('logs'):
        os.mkdir('logs')
    fh = RotatingFileHandler('logs/main_app.log',maxBytes=1024*20,backupCount=15)
    fh.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(fh)
    app.logger.setLevel(logging.INFO)
    app.logger.info('The application started')


# Creating the flask app and binding the configuration class to it
app = Flask(__name__)
app.config.from_object(Config)

# Post-app-creating initilization
login_manager = LoginManager(app)
login_manager.login_view = 'login'
Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

if not app.debug:
    setup_file_logging()
from app import routes, models, errors
