from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

#Creating the flask app and binding the configuration class to it
app = Flask(__name__)
app.config.from_object(Config)

#Post-app-creating initilization
login_manager = LoginManager(app)
Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes,models

