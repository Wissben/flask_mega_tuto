from app import app
from flask import jsonify,render_template,request,abort,redirect,url_for,Response
import os
import random
import soundfile as sf
import wave
import struct
from time import sleep

from threading import Timer
# from app.additional import parse_audio
from app.login import LoginForm
from app.settings import APP_STATIC

AUTHORIZED_EXTENSIONS = ['wav','mp3']
app.config['UPLOAD_FOLDER']='.'
PROBAS = []
DATA =[]



@app.route('/')
@app.route('/index')
def index():
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
    Dummy function to return a random 
    '''
    return jsonify({'model' : 'screame_detector','proba': random.random()}) 


@app.route('/audio/uploader',methods = ['POST', 'GET'])
def upload_secure():
    # print('entered ')
    if request.method == 'POST':
        f = request.files['audio_file']
        if (allowed_extensions(f.filename)):
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
            return redirect('/classify')
        else:
            print('here my friend here')
            return redirect('/')

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html',title='Sign in',form=form)

def gen(wave_file):
    # one_second = int(wave_file.getnframes()/wave_file._framerate)
    for i in range(wave_file.getnframes()):
        frame = wave_file.readframes(1)
        if(i%wave_file._framerate==0):
            yield str({'second ': i/wave_file._framerate,'proba':random.random()})+"\n"

@app.route('/audio_feed')
def video_feed():
    wave_file = wave.open('/home/weiss/CODES/BM/intent_gatherer/flask_backend/app/static/test.wav', 'r')
    return Response(gen(wave_file),
                    mimetype='text')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
