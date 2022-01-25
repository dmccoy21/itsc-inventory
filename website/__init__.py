from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# creates instance of db (database)
db = SQLAlchemy()
# set name of database
DB_NAME = "database.db"


def create_app():
    # allows for python main.py terminal command
    app = Flask(__name__)
    # secret key - non-empty string
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    # configure database link
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    # for terminal optimization only
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.init_app(app)

    from .routes import routes
    from .auth import auth

    # links routes and auth paths
    app.register_blueprint(routes, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Ticket

    # one-time creation of app's database
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    # if the database hasn't been created yet...
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
