import os
import random
import wave
from datetime import datetime
from time import sleep

import numpy as np
from flask import Response
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_babel import get_locale
from flask_login import current_user, login_required
from flask_socketio import emit
from guess_language import guess_language
from librosa.feature import mfcc
from scipy.io import wavfile

import app.utils as utils
from app import db
from app import socketio
from app.main import bp
from app.main.forms import EditProfileForm, PostForm
from app.models import User, Post
from config import APP_STATIC, APP_BASE_DIR

AUTHORIZED_EXTENSIONS = ['mp3', 'wav']


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKKNOWN' or len(language) > 5:
            language = ''
        post = Post(content=form.post.data, author=current_user, language=language)
        print('CURRENT POST ', form.post.data)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been added')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.post_feed().paginate(page, current_app.config['MAX_POST_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    print('[INFO] : the query result is {}'.format(posts))
    return render_template('index.html', form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    all_posts = Post.query.paginate(page, current_app.config['MAX_POST_PER_PAGE'], False)
    next_url = url_for('main.explore', page=all_posts.next_num) if all_posts.has_next else None
    prev_url = url_for('main.explore', page=all_posts.prev_num) if all_posts.has_prev else None
    return render_template('index.html', posts=all_posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/upload_file')
@login_required
def upload_file():
    """
    rendering the upload template
    :return:
    """
    return render_template('upload.html')


def allowed_extensions(extension):
    '''
    Check if a given string (extension) is allowed as file format
    Obviously an extensionless file is prohibited
    '''
    return '.' in extension and extension.rsplit('.', 1)[1].lower() in AUTHORIZED_EXTENSIONS


@bp.route('/classify')
@login_required
def inference():
    '''
    Dummy route to return a random probability evaluation
    '''
    return jsonify({'model': 'screame_detector', 'proba': random.random()})


@bp.route('/audio/uploader', methods=['POST', 'GET'])
@login_required
def upload_secured():
    '''
    Route for uploading the audio file after checking its authenticity and validity
    '''
    if request.method == 'POST':
        f = request.files['audio_file']
        if (allowed_extensions(f.filename)):
            f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], f.filename))
            return redirect(url_for('main.audio_feed', filename=f.filename))
        else:
            print('here my friend here')
            return redirect('/')


@bp.route('/user/<string:username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.post_feed().paginate(page, current_app.config['MAX_POST_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    print('[INFO] : the query result is {}'.format(posts))
    return render_template('profile.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow().astimezone()
        db.session.commit()
    g.locale = str(get_locale())


@bp.route('/user/<string:username>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Changes saved !')
        return redirect(url_for('main.user', username=form.username.data))
    if request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit profile', form=form)


@bp.route('/follow/<string:username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('The user {} does not exists'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself !')
        return redirect(url_for('main.index'))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following {}, best of wishes'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<string:username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('The user {} does not exists'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself !')
        return redirect(url_for('main.index'))
    current_user.unfollow(user)
    db.session.commit()
    flash('Sadly you just lost {} as a friend '.format(username))
    return redirect(url_for('main.user', username=username))


def audio_parsing_generator(wave_file):
    '''
    Generator for parsing an audio file, returns dummy probability for now
    '''
    seconds = int(wave_file.getnframes() / wave_file._framerate)
    print('[INFO] : seconds = ', seconds)
    for i in range(seconds):
        frame = wave_file.readframes(1)
        arr = np.array(list(frame), dtype='float32')
        mfcc_matrix = mfcc(arr, sr=wave_file._framerate, n_mfcc=26)
        print('[INFO] current frame is {}'.format(arr))
        predictions = utils.make_tf_serving_request(mfcc_matrix.flatten().tolist(),
                                                    'http://localhost:8051/v1/models/test_model')
        # Do stuff to the frame
        # foo(frame)
        sleep(1)
        yield {'second ': i, 'proba': predictions[0]}


def stream_template(template_name, **context):
    current_app.update_template_context(context)
    t = current_app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.disable_buffering()
    return rv


@bp.route('/audio_feed/<string:filename>')
@login_required
def audio_feed(filename):
    """
    Route for itterating over an audio file and send it to a parsing function
    :param filename: the name of the file
    :type filename: str
    :return:
    """
    wave_file = wave.open(os.path.join(APP_STATIC, filename), 'r')
    file_probas = audio_parsing_generator(wave_file)
    return Response(stream_template('realtime.html', probas=file_probas))


@bp.route('/live_audio')
@login_required
def live_audio_feed():
    return render_template('live_audio_stream.html')


@socketio.on('json')
def handle_message(json_message):
    """
    Function to handle the recieved data from the client side, in this case the data is sent to a served
    tensorflow model which will now return a dummy random prediction
    :param json_message: the audio data and meta-data
    :type json_message: dict
    :return: None
    """
    chunks = np.array([b for b in json_message.values()], dtype='float32')
    wavfile.write(os.path.join(APP_BASE_DIR, 'test.wav'), 44100, chunks)
    mfcc_matrix = mfcc(chunks, n_mfcc=26, sr=16384)
    predictions = utils.make_tf_serving_request(mfcc_matrix.flatten().tolist(),
                                                'http://localhost:8051/v1/models/test_model')
    print('[INFO] : RECIEVED  {} FROM TENSORFLOW SERVER'.format(predictions))
    emit('recieve', {'proba': predictions[0]})
