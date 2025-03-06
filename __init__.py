from flask import Flask
from .extensions import db, migrate, login_manager, mail
from .config import Config
from .routes.shipping import shipping
from .routes.user import user
from .routes.employee import employee

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Регистрируем Blueprint
    app.register_blueprint(user)
    app.register_blueprint(shipping)
    app.register_blueprint(employee)

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)  # <-- Добавлено

    # LOGIN MANAGER
    login_manager.login_view = 'user.login'
    login_manager.login_message = 'У вас нет доступа к данной стр.'

    with app.app_context():
        db.create_all()

    return app
