from app import app
from app.login import LoginForm
from app.config import APP_STATIC
from app.models import User,Post
from flask import flash,jsonify,render_template,request,abort,redirect,url_for,Response
from time import sleep
from flask_login import current_user,login_user,logout_user
from werkzeug


import os
import random
import wave


AUTHORIZED_EXTENSIONS = ['wav','mp3']
app.config['UPLOAD_FOLDER']=os.path.join(APP_STATIC)
PROBAS = []
DATA =[]

@app.route('/')
@app.route('/index')
def index():
    return render_template('base.html')

@app.route('/upload_file')
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
    return '.' in extension and extension.rsplit('.',1)[1].lower() in AUTHORIZED_EXTENSIONS

@app.route('/classify')
def inference():
    '''
    Dummy route to return a random probability evaluation
    '''
    return jsonify({'model' : 'screame_detector','proba': random.random()}) 


@app.route('/audio/uploader',methods = ['POST', 'GET'])
def upload_secure():
    '''
    Route for uploading the audio file after checking its authenticity and validity
    '''
    if request.method == 'POST':
        f = request.files['audio_file']
        if (allowed_extensions(f.filename)):
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
            return redirect(url_for('video_feed',filename=f.filename))
        else:
            print('here my friend here')
            return redirect('/')

@app.route('/login',methods=['POST','GET'])
def login():
    '''
    Route for user auhentification
    '''

    if current_user.is_authenticated :
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        print ('[DEBUG] : login request from {} with the flag {} to {}'.format(
            form.username.data,
            form.remember_me.name,
            form.remember_me.data
        ))
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            print(['[ERROR] : Wrong password or username'])
            return redirect(url_for('login'))
        login_user(user,remember=form.remember_me.data)
        next_route = request.args.get('next')
        if not next_route or url
        return redirect(url_for('index'))
    return render_template('login.html',title='Sign in',form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
def gen(wave_file):
    '''
    Generator for parsing an audio file, returns dummy probability for now
    '''
    seconds = int(wave_file.getnframes()/wave_file._framerate)
    print('[INFO] : seconds = ',seconds)
    for i in range(seconds):
        frame = wave_file.readframes(1)
        #Do stuff to the frame
        #foo(frame)
        sleep(1)
        yield {'second ': i,'proba':random.random()}

def stream_template(template_name, **context):                                                                                                                                                 
    app.update_template_context(context)                                                                                                                                                       
    t = app.jinja_env.get_template(template_name)                                                                                                                                              
    rv = t.stream(context)                                                                                                                                                                     
    rv.disable_buffering()                                                                                                                                                                     
    return rv 


@app.route('/audio_feed/<string:filename>')
def video_feed(filename):
    '''
    Route for itterating over an audio file and send it to a parsing function
    '''
    wave_file = wave.open(os.path.join(APP_STATIC,filename), 'r')
    print("SOMETHING")
    file_probas = gen(wave_file)                                                                                                                                                                          
    return Response(stream_template('realtime.html', probas=file_probas))


