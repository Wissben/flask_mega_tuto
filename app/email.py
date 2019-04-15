from flask_mail import Message
from flask import render_template
from app import mail,app
from threading import Thread


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_mail(subject, sender, recipents, text_body, html_body):
    message = Message(subject=subject, sender= sender,recipients=recipents, body=text_body, html=html_body)
    Thread(target=send_async_email,args=(app,message)).start()

def send_password_reset_email(user):
    token = user.get_reset_pass_token()
    print(app.config['ADMINS'])
    send_mail(subject='[Supa Blogu postu] Reset your password',
              sender=app.config['ADMINS'][0],
              recipents=[user.email],
              html_body=render_template('reset_password_message.html',user=user,token=token),
              text_body=render_template('reset_pass_mail_text.txt',user=user,token=token))