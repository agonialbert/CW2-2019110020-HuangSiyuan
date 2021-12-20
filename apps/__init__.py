from flask import Flask
from flask.logging import default_handler
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from datetime import timedelta
from flask_mail import Mail
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

# logging.basicConfig(filename='record.log', level=logging.DEBUG,
#                     format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


@app.before_first_request
def before_first_request():
    log_level = logging.INFO
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(filename)s %(funcName)s[line:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %X"
    )
    for handler in app.logger.handlers:
        app.logger.removeHandler(handler)
    root = os.path.dirname(os.path.abspath(__file__))
    logdir = os.path.join(root, 'logs')
    if not os.path.exists(logdir):
        os.mkdir(logdir)
    log_file = os.path.join(logdir, 'app.log')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)
    for logger in (
            app.logger,
            logging.getLogger('sqlalchemy'),
            logging.getLogger('other_package'),
    ):
        logger.addHandler(default_handler)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.permanent_session_lifetime = timedelta(minutes=20)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['ENV'] = 'development'
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()

# mail
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_ADDRESS')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')
mail = Mail(app)
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

csrf = CSRFProtect(app)
jinja_options = ImmutableDict(
    extensions=[
        'jinja2.ext.autoescape', 'jinja2.ext.with_'  # Turn auto escaping on
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
