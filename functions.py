import os
import secrets
from PIL import Image

from flask import current_app
from flask_mail import Message
from .extensions import mail


def send_email(subject, recipient, body):
    msg = Message(subject, recipients=[recipient])
    msg.body = body

    try:
        mail.send(msg)
        print("Email успешно отправлен!")
    except Exception as e:
        print(f"Ошибка при отправке email: {str(e)}")

def save_picture(picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.config["SERVER_PATH"], picture_fn)




    output_size = (100, 100)
    i = Image.open(picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

