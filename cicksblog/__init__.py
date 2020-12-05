from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_login import LoginManager
from cicksblog.config import Config

# database
db = SQLAlchemy()
# migrate
migrate = Migrate()
# bcrypt
bcrypt = Bcrypt()
# login manager
login_manager = LoginManager()
login_manager.login_view = "users.login"
# mail
mail = Mail()


def create_app(config_class=Config):
    # app
    app = Flask(__name__)

    # configuration app
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # import BluePrint
    from cicksblog.users.routes import users
    from cicksblog.posts.routes import posts
    from cicksblog.main.routes import main
    from cicksblog.errors.handlers import errors

    # registering blueprint
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app