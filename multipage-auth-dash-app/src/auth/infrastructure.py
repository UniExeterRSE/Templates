import os

from flask import Flask
from flask_login import LoginManager, UserMixin
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from config import get_config

"""Authentication infrastructure module providing Flask app setup and database configuration.

This module contains the core infrastructure components for the authentication system:
- User: A user model to store user information in the database
- server: The Flask server instance with configuration
- user_db: The SQLAlchemy database instance for user management
- login_manager: The Flask-Login login manager object
- load_user: A function to load a user from the database by ID
- Database initialization and table creation"""

# Create the Flask server and configure it using the centralized config
server = Flask(__name__)
config = get_config()
server.config.update(config)

# Initialize Flask-Session
Session(server)

# Create the SQLAlchemy db instance for user management
user_db = SQLAlchemy()


class User(UserMixin, user_db.Model):
    """A user model to store user information in the database

    Inherits from UserMixin (Flask-Login UserMixin class for user management
    functionalities) and user_db.Model (a SQLAlchemy Model class for database
    management).
    """

    id = user_db.Column(user_db.Integer, primary_key=True)
    username = user_db.Column(user_db.String(80), unique=True, nullable=False)
    hashed_password = user_db.Column(user_db.String(120), nullable=False)

    def __init__(self, username, hashed_password):
        self.username = username
        self.hashed_password = hashed_password


# Initialize SQLAlchemy with the Flask server
user_db.init_app(server)

# Login manager object will be used to login / logout users
login_manager = LoginManager()
login_manager.init_app(server)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Only create tables if the database file does not exist
db_path = server.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
if not os.path.exists(db_path):
    with server.app_context():
        user_db.create_all()
