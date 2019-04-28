from flask import render_template, current_app

from app.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_pass_token()
    print(current_app.config['ADMINS'])
    send_email(subject='[Supa Blogu postu] Reset your password', sender=bp.config['ADMINS'][0], recipents=[user.email],
               text_body=render_template('auth/reset_pass_mail_text.txt', user=user, token=token),
               html_body=render_template('auth/reset_password_message.html', user=user, token=token))
