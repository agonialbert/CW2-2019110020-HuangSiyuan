from flask import Flask, request
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from datetime import timedelta

from flask_wtf import CSRFProtect
from werkzeug.datastructures import ImmutableDict
from flask_script import Manager
import os
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
import logging
# from logging import FileHandler
# logging.basicConfig(filename='app.log', level=logging.DEBUG,
#                     format=' %(asctime) s %(levelname) s %(name) s %(threadName) s : %(message) s')

app = Flask(__name__, template_folder='../templates', static_folder='../static')


@app.before_first_request
def before_first_request():
    log_level = logging.INFO

    for handler in app.logger.handlers:
        app.logger.removeHandler(handler)
    root = os.path.dirname(os.path.abspath(__file__))
    logdir = os.path.join(root, 'logs')
    if not os.path.exists(logdir):
        os.mkdir(logdir)
    log_file = os.path.join(logdir, 'app.log')
    handler = logging.FileHandler(log_file)
    handler.setLevel(log_level)
    app.logger.addHandler(handler)

    app.logger.setLevel(log_level)
    # app.logger.format(' %(asctime) s %(levelname) s %(name) s %(threadName) s : %(message) s')


app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.permanent_session_lifetime = timedelta(minutes=20)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['ENV'] = 'development'
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)


# csrf = CSRFProtect(app)
jinja_options = ImmutableDict(
 extensions=[
  'jinja2.ext.autoescape', 'jinja2.ext.with_' #Turn auto escaping on
 ])

# Autoescaping depends on you
app.jinja_env.autoescape = True | False


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
manager = Manager(app=app)
Migrate(app=app, db=db)
manager.add_command('db', MigrateCommand)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
from apps import routes
from apps import models

