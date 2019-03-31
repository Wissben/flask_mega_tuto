
import numpy as np
import shutil
import sounddevice as sd
import soundfile as sf
import os
# from app.settings import APP_STATIC


from time import sleep
 
SAMPLE_RATE = 44100.0 

def get_audio_duration(fd):
    return (len(fd) / fd.samplerate)

def fall_back_callback(indata, frames, time, status):
            print("[INFO] : FALLBACK CALLBACK entered with sample rate = " , SAMPLE_RATE)

def main(file_path='../static/test.wav',callback=fall_back_callback):
# def main(file_path=os.path.join(APP_STATIC,'test.wav'),callback=fall_back_callback):
    try:
        fd = sf.SoundFile('../static/test.wav')
        # fd = sf.SoundFile(os.path.join(APP_STATIC,file_path))
        LEN_MAX  = int(get_audio_duration(fd))
        print('[INFO] : duration is ',LEN_MAX)
            
        curren_callback = callback if callback is not None else fall_back_callback

        with sd.InputStream(channels=1, callback=callback,
                            blocksize=int(SAMPLE_RATE * 1000 / 1000),
                            samplerate=SAMPLE_RATE):
            seconds = 1
            while True:
                sleep(1)
                seconds+=1
                if seconds > LEN_MAX:
                    break
    except KeyboardInterrupt:
        exit(0)
    except FileNotFoundError:
        print("[ERROR] : File {} not found".format(fd))
    except Exception as e:
        print(e)
        print('[ERROR] : Something happened')

main()