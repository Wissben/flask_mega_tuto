from threading import Thread

from flask import current_app
from flask_mail import Message

from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipents, text_body, html_body):
    message = Message(subject=subject, sender=sender, recipients=recipents, body=text_body, html=html_body)
    Thread(target=send_async_email, args=(current_app, message)).start()
