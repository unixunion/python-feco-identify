#!/usr/bin/env python

import numpy as np
import librosa
import librosa.display
import time
import pyaudio
import scipy
import matplotlib.pyplot as plt

input_device = pyaudio.PyAudio()
rate = int(input_device.get_default_input_device_info()['defaultSampleRate']) #sampling rate
chunksize = 16384
stream = input_device.open(format=pyaudio.paFloat32, channels=1, rate=rate, input=True, frames_per_buffer=chunksize)
SILENCE = 0.004

def getmillis():
    return int(round(time.time() * 1000))

def get_sample():
    stream.start_stream()
    start = getmillis()
    rawdata = stream.read(chunksize)
    data = np.zeros(chunksize)
    sampling = False
    while 1:

        # TODO FIXME
        # when first sample peak detected, concat the previous "silence sample" to the head.
        # when wrapping up, add one silence sample at the end.
    
        newchunk = stream.read(chunksize)
        # if rawdata is None and sampling:
        #     print("creating new")
        #     rawdata = newchunk
        if not sampling and (np.amax(np.frombuffer(newchunk, dtype=np.float32)) > SILENCE or np.amin(np.frombuffer(newchunk, dtype=np.float32)) < -1 * SILENCE):
            print("new sample")
            # rawdata = newchunk
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

    data = np.frombuffer(rawdata, np.float32)
    end1 = getmillis()
    stream.stop_stream()
    return data, rate

# Load the example clip
y, sr = get_sample()

#print("%s, %s" % (y, sr))

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


plt.figure(figsize=(6, 4))
librosa.display.specshow(librosa.power_to_db(S, ref=np.max),
                         y_axis='mel', x_axis='time', sr=sr,
                         hop_length=hop_length, fmin=fmin, fmax=fmax)
plt.tight_layout()

plt.show()