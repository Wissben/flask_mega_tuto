import os
import subprocess
import time

PIPE_NAME = 'pipe_test'



def child( ):
    pipeout = os.open(PIPE_NAME, os.O_WRONLY)
    cmd = "ffmpeg -y -i hw:0 pipe:1".split()
    subprocess.Popen(cmd,stdout=pipeout)
def parent( ):
    pipein = open(PIPE_NAME, 'r')
    while True:
        time.sleep(1)
        line = pipein.readline()
        print(line)
if not os.path.exists(PIPE_NAME):
    os.mkfifo(PIPE_NAME)
pid = os.fork()
if pid != 0:
    parent()
else:
    child()
# cmd = "ffmpeg -f alsa -i hw:0".split()
# ps = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
# output = subprocess.check_output(['grep', 'chrome'], stdin=ps.stdout)
# ps.wait()
