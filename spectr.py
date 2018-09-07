#!/usr/bin/env python
import sys

############### Import Libraries ###############
from matplotlib.mlab import window_hanning,specgram
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LogNorm
import numpy as np
import time

############### Import Modules ###############
import pyaudio
input_device = pyaudio.PyAudio()

############### Constants ###############
SAMPLES_PER_FRAME = 10 #Number of mic reads concatenated within a single window
nfft = 1024 #NFFT value for spectrogram
overlap = 512 #overlap value for spectrogram
rate = int(input_device.get_default_input_device_info()['defaultSampleRate']) #sampling rate
chunksize = 512
SILENCE = 400

# IO
stream = input_device.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=chunksize)
data = np.zeros(chunksize+1)

############### Functions ###############
"""
get millis
"""
def getmillis():
    return int(round(time.time() * 1000))


"""
get_sample:
gets the audio data from the microphone
inputs: audio stream and PyAudio object
outputs: int16 array
"""
def get_sample():
    stream.start_stream()
    start = getmillis()
    rawdata = np.zeros(chunksize)
    data = np.zeros(chunksize)
    sampling = False
    while 1:
    
        newchunk = stream.read(chunksize)
        # if rawdata is None and sampling:
        #     print("creating new")
        #     rawdata = newchunk
        if not sampling and np.amax(np.fromstring(newchunk, dtype=np.int16)) > SILENCE or np.amin(np.fromstring(newchunk, dtype=np.int16)) < -1 * SILENCE:
            print("new sample")
            rawdata = newchunk
            sampling = True
            print("sampling, max: %s, min: %s" % (np.amax(np.fromstring(newchunk, dtype=np.int16)), np.amin(np.fromstring(newchunk, dtype=np.int16))))
        elif sampling:
            print("sampling")
            np.append(rawdata, newchunk)
    
        if sampling and (np.amax(np.fromstring(newchunk, dtype=np.int16)) < SILENCE or np.amin(np.fromstring(newchunk, dtype=np.int16)) > -1 * SILENCE):
            print("going idle")
            break

        # else:
            # print("done, max: %s, min: %s" % (np.amax(np.fromstring(newchunk, dtype=np.int16)), np.amin(np.fromstring(newchunk, dtype=np.int16))))
            # break
    data = np.fromstring(rawdata,np.int16)
    end1 = getmillis()
    stream.stop_stream()
    return data
"""
get_specgram:
takes the FFT to create a spectrogram of the given audio signal
input: audio signal, sampling rate
output: 2D Spectrogram Array, Frequency Array, Bin Array
see matplotlib.mlab.specgram documentation for help
"""
def get_specgram(signal,rate):
    print("signal:%s\n,rate:%s\n,nfft:%s\n,overlap:%s\n" % (signal, rate, nfft, overlap))
    arr2D,freqs,bins = specgram(signal,window=window_hanning,
                                Fs = rate,NFFT=nfft,noverlap=overlap)
    return arr2D,freqs,bins

"""
update_fig:
updates the image, just adds on samples at the start until the maximum size is
reached, at which point it 'scrolls' horizontally by determining how much of the
data needs to stay, shifting it left, and appending the new data. 
inputs: iteration number
outputs: updated image
"""
def update_fig(n):
    data = get_sample()
    arr2D,freqs,bins = get_specgram(data,rate)
    im_data = im.get_array()
    if n < SAMPLES_PER_FRAME:
        im_data = np.hstack((im_data,arr2D))
        im.set_array(im_data)
    else:
        keep_block = arr2D.shape[1]*(SAMPLES_PER_FRAME - 1)
        im_data = np.delete(im_data,np.s_[:-keep_block],1)
        im_data = np.hstack((im_data,arr2D))
        im.set_array(im_data)
    return im,

############### Initialize Plot ###############
fig = plt.figure()
"""
Launch the stream and the original spectrogram
"""
data = get_sample()
arr2D,freqs,bins = get_specgram(data,rate)
"""
Setup the plot paramters
"""
extent = (bins[0],bins[-1]*SAMPLES_PER_FRAME,freqs[-1],freqs[0])
im = plt.imshow(arr2D,aspect='auto',extent = extent,interpolation="none",
                cmap = 'jet',norm = LogNorm(vmin=.01,vmax=1))
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.title('Real Time Spectogram')
plt.gca().invert_yaxis()
##plt.colorbar() #enable if you want to display a color bar

############### Animate ###############
anim = animation.FuncAnimation(fig,update_fig,blit = False,
                               interval=64)
try:
    plt.show()
except:
    print("Plot Closed")

############### Terminate ###############
stream.stop_stream()
stream.close()
print("Program Terminated")

