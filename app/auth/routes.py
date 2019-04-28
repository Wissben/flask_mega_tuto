from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse

from app import db
from app.auth import bp
from app.auth.email import send_password_reset_email
from app.auth.forms import LoginForm, ResetPasswordForm, RequestNewPassWordForm
from app.models import User


@bp.route('/login', methods=['POST', 'GET'])
def login():
    '''
    Route for user auhentification
    '''

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        # for debugging only
        print('[DEBUG] : login request from <{}> with the flag <{}> to <{}>'.format(
            form.username.data,
            form.remember_me.name,
            form.remember_me.data
        ))

        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            # wron email/username or password
            flash('wrong email or password')
            print('[ERROR] : wrong email or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_route = request.args.get('next')
        print('[INFO] : next page is ', next_route)
        if not next_route or url_parse(next_route).netloc != '':
            return redirect(url_for('index'))
        return redirect(next_route)
    return render_template('auth/login.html', title='Sign in', form=form, authentification_error=False)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@bp.route('/reset_password_request', methods=['POST', 'GET'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestNewPassWordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print('[INFO] : user {} found'.format(user))
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


@bp.route('/reset_pass/<string:token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if (current_user.is_authenticated):
        flash('You must logout to register')
        return redirect(url_for('/index'))
    signup_form = SignUpForm()
    if signup_form.validate_on_submit():
        user_to_add = User(username=signup_form.username.data, email=signup_form.email.data)
        user_to_add.set_password(signup_form.password.data)
        db.session.add(user_to_add)
        db.session.commit()
        flash(
            'Happy to have you with us {} please check your email for a verification link and some more informaton'.format(
                user_to_add.username
            ))
        return redirect(url_for('auth.login'))
    return render_template('auth/signup.html', form=signup_form)
