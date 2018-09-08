import numpy as np
import librosa
import librosa.display
import time
import pyaudio
import scipy
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LogNorm
from threading import Thread

input_device = pyaudio.PyAudio()
rate = int(input_device.get_default_input_device_info()['defaultSampleRate']) #sampling rate
chunksize = 16384
stream = input_device.open(format=pyaudio.paFloat32, channels=1, rate=rate, input=True, frames_per_buffer=chunksize)
SILENCE = 0.1

def getmillis():
    return int(round(time.time() * 1000))

def get_sample():
    stream.start_stream()
    start = getmillis()
    rawdata = stream.read(chunksize)
    data = np.zeros(chunksize)
    sampling = False

    while 1:
        newchunk = stream.read(chunksize)
        if not sampling and (np.amax(np.frombuffer(newchunk, dtype=np.float32)) > SILENCE or np.amin(np.frombuffer(newchunk, dtype=np.float32)) < -1 * SILENCE):
            print("new sample")
            np.append(rawdata, newchunk)
            sampling = True
            print("sampling, max: %s, min: %s" % (np.amax(np.frombuffer(newchunk, dtype=np.float32)), np.amin(np.frombuffer(newchunk, dtype=np.float32))))
        elif sampling:
            print("sampling, max: %s, min: %s" % (np.amax(np.frombuffer(newchunk, dtype=np.float32)), np.amin(np.frombuffer(newchunk, dtype=np.float32))))
            np.append(rawdata, newchunk)
        if sampling and np.amax(np.frombuffer(newchunk, dtype=np.float32)) < SILENCE and np.amin(np.frombuffer(newchunk, dtype=np.float32)) > (-1 * SILENCE):
            print("final sample, max: %s, min: %s" % (np.amax(np.frombuffer(newchunk, dtype=np.float32)), np.amin(np.frombuffer(newchunk, dtype=np.float32))))
            print("final sample, threshold max: %s, min: %s" % (np.amax(np.frombuffer(newchunk, dtype=np.float32)<SILENCE), np.amin(np.frombuffer(newchunk, dtype=np.float32))>(-1*SILENCE)))
            print("going idle")
            np.append(rawdata, newchunk)
            break
        else:
            print("idle, max: %s, min: %s" % (np.amax(np.frombuffer(newchunk, dtype=np.float32)), np.amin(np.frombuffer(newchunk, dtype=np.float32))))

        # if getmillis() - start > 1000:
        #     print("timeout")
        #     break

    data = np.frombuffer(rawdata, np.float32)
    end1 = getmillis()
    stream.stop_stream()
    return data, rate


def monitorAudio(threadname):
    global y, sr
    while 1:
        try:
            y, sr = get_sample()
        except Exception as e:
            print("error %s" % e)
            raise Exception("Crash")


def update_fig(n):
    # y, sr = get_sample()
    print("updating figure")
    global y, sr, im
    hop_length = int(librosa.time_to_samples(1./200, sr=sr))
    S = librosa.feature.melspectrogram(y, sr=sr, n_fft=n_fft,
                                   hop_length=hop_length,
                                   fmin=fmin,
                                   fmax=fmax,
                                   n_mels=n_mels)

    # librosa.display.specshow(librosa.power_to_db(S, ref=np.max),
    #                     y_axis='mel', x_axis='time', sr=sr,
    #                     hop_length=hop_length, fmin=fmin, fmax=fmax)
    im.set_array(S)
    
    return im,

fig = plt.figure()
# plt.figure(figsize=(6, 4))
y, sr = get_sample()
ims = []

thread1 = Thread(target=monitorAudio, args=("MonitorAudio-1",))
thread1.daemon = True
thread1.start()

# Load the example clip

n_fft = 1024
hop_length = int(librosa.time_to_samples(1./200, sr=sr))
lag = 2
n_mels = 138
fmin = 27.5
fmax = 16000.
max_size = 3

print("hop_length: %s" % hop_length)

S = librosa.feature.melspectrogram(y, sr=sr, n_fft=n_fft,
                                   hop_length=hop_length,
                                   fmin=fmin,
                                   fmax=fmax,
                                   n_mels=n_mels)

im = plt.imshow(S, aspect='auto', interpolation="none", cmap = 'jet', animated=True)

# plt.colorbar(format='%+2.0f dB')
# plt.title('Power spectrogram')
plt.tight_layout()

# librosa.display.specshow(librosa.power_to_db(S, ref=np.max),
#                          y_axis='mel', x_axis='time', sr=sr,
#                          hop_length=hop_length, fmin=fmin, fmax=fmax)

# plt.tight_layout()

anim = animation.FuncAnimation(fig, update_fig, blit=True, interval=64)

try:
    plt.show()
except:
    print("Plot Closed")

############### Terminate ###############
stream.stop_stream()
stream.close()
print("Program Terminated")