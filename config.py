import os

class Config(object):
    APPNAME = 'app'
    ROOT = os.path.abspath(APPNAME)
    UPLOADS_PATH = '/static/upload/'
    SERVER_PATH = ROOT + UPLOADS_PATH

    USER = os.environ.get('POSTGRES_USER', 'user')
    PASSWORD = os.environ.get('POSTGRES_PASSWORD', '448448')
    HOST = os.environ.get('POSTGRES_HOST', '127.0.0.1')
    PORT = os.environ.get('POSTGRES_PORT', '5432')
    DB = os.environ.get('POSTGRES_DB', 'mydb')

    SQLALCHEMY_DATABASE_URI = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"
    SECRET_KEY = '1KEY_2secret2_KEY2_2SECRET2_RESKET1'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # Настройки для Flask-Mail
    MAIL_SERVER = 'smtp.gmail.com'  # SMTP сервер (можно поменять на другой)
    MAIL_PORT = 587  # Порт для TLS
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'your_email@gmail.com')  # Почта
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'your_email_password')  # Пароль
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
