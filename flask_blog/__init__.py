from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from flask_blog.config import Config

app = Flask(__name__)
# sets base_dir to the base directory of the package
# designate path (URI) for SQLite database
# in CMD:
# py > import secrets > secrets.token_hex(16)
# secret key:
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message_category = 'info'

# import the routes
from flask_blog.users.routes import users  # noqa
from flask_blog.posts.routes import posts  # noqa
from flask_blog.main.routes import main  # noqa

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)
