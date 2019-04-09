import os
import random
import wave
from datetime import datetime
from time import sleep

from flask import flash, jsonify, render_template, request, redirect, url_for, Response
from flask_login import current_user, login_user, logout_user, login_required
from flask_socketio import emit
from werkzeug.urls import url_parse

from app import app, db
from app import socketio
from app.config import APP_STATIC
from app.forms import LoginForm, SignUpForm, EditProfileForm, PostForm
from app.models import User, Post

AUTHORIZED_EXTENSIONS = ['wav', 'mp3']
app.config['UPLOAD_FOLDER'] = os.path.join(APP_STATIC)
PROBAS = []
DATA = []


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(content=form.post.data, author=current_user)
        print('CURRENT POST ',form.post.data)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been added')
        return redirect(url_for('index'))
    posts = current_user.post_feed().all()
    return render_template('index.html', form=form, posts=posts)


@app.route('/upload_file')
@login_required
def upload_file():
    '''
    Main route for rendering the front-page of the web app
    '''
    return render_template('upload.html')


def allowed_extensions(extension):
    '''
    Check if a given string (extension) is allowed as file format
    Obviously an extensionless file is prohibited
    '''
    return '.' in extension and extension.rsplit('.', 1)[1].lower() in AUTHORIZED_EXTENSIONS


@app.route('/classify')
@login_required
def inference():
    '''
    Dummy route to return a random probability evaluation
    '''
    return jsonify({'model': 'screame_detector', 'proba': random.random()})


@app.route('/audio/uploader', methods=['POST', 'GET'])
@login_required
def upload_secure():
    '''
    Route for uploading the audio file after checking its authenticity and validity
    '''
    if request.method == 'POST':
        f = request.files['audio_file']
        if (allowed_extensions(f.filename)):
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
            return redirect(url_for('video_feed', filename=f.filename))
        else:
            print('here my friend here')
            return redirect('/')


@app.route('/login', methods=['POST', 'GET'])
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
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_route = request.args.get('next')
        print('[INFO] : next page is ', next_route)
        if not next_route or url_parse(next_route).netloc != '':
            return redirect(url_for('index'))
        return redirect(next_route)
    return render_template('login.html', title='Sign in', form=form, authentification_error=False)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
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
        return redirect(url_for('login'))
    return render_template('signup.html', form=signup_form)


@app.route('/user/<string:username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.id == user.id:
        posts = [
            {'author': user, 'content': 'Test post #1'},
            {'author': user, 'content': 'Test post #2'}
        ]
        avatar = user.generate_avatar(128)
        return render_template('profile.html', user=user, posts=posts)
    return render_template('profile.html', user=user, posts=[{'author': user, 'content': 'Test another one#1'},
                                                             ])


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow().astimezone()
        db.session.commit()


@app.route('/user/<string:username>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Changes saved !')
        return redirect(url_for('user', username=form.username.data))
    if request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit profile', form=form)


@app.route('/follow/<string:username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('The user {} does not exists'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself !')
        return redirect(url_for('index'))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following {}, best of wishes'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<string:username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('The user {} does not exists'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself !')
        return redirect(url_for('index'))
    current_user.unfollow(user)
    db.session.commit()
    flash('Sadly you just lost {} as a friend '.format(username))
    return redirect(url_for('user', username=username))


def gen(wave_file):
    '''
    Generator for parsing an audio file, returns dummy probability for now
    '''
    seconds = int(wave_file.getnframes() / wave_file._framerate)
    print('[INFO] : seconds = ', seconds)
    for i in range(seconds):
        frame = wave_file.readframes(1)
        # Do stuff to the frame
        # foo(frame)
        sleep(1)
        yield {'second ': i, 'proba': random.random()}


def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.disable_buffering()
    return rv


@app.route('/audio_feed/<string:filename>')
@login_required
def video_feed(filename):
    '''
    Route for itterating over an audio file and send it to a parsing function
    '''
    wave_file = wave.open(os.path.join(APP_STATIC, filename), 'r')
    file_probas = gen(wave_file)
    return Response(stream_template('realtime.html', probas=file_probas))


@app.route('/live_audio')
@login_required
def live_audio_feed():
    return render_template('live_audio_stream.html')


#
@socketio.on('json')
def handle_message(json):
    print('[INFO] : recieved chunk of data : ', str(json))
    emit('recieve', {'proba': random.random()})
