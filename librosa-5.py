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
from scipy import signal

input_device = pyaudio.PyAudio()
rate = int(input_device.get_default_input_device_info()['defaultSampleRate'])
chunksize = 512
dynamic_silence = -1000
y = np.ones(20000)

audio_buffer = []
data = np.ones(20000)

# thread that records audio samples into the audio_buffer
def audio_monitor(threadname):
    stream = input_device.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=chunksize)
    stream.start_stream()
    while True:
        try:
            audio_buffer.append(stream.read(chunksize))
        except Exception as e:
            print("failure was always an option!")
            stream.stop_stream()
            stream.close()
            stream = input_device.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=chunksize)
            stream.start_stream()


def audio_silence_autoleveling(threadname):
    global dynamic_silence
    while True:
        try:
            min_level = 0
            max_level = 0
            for newchunk in audio_buffer:
                if np.amin(np.frombuffer(newchunk, dtype=np.int16)) < min_level:
                    min_level = np.amin(np.frombuffer(newchunk, dtype=np.int16))
                    print("new min level: %s" % min_level)
                if np.amax(np.frombuffer(newchunk, dtype=np.int16)) > max_level:
                    max_level = np.amax(np.frombuffer(newchunk, dtype=np.int16))
                    print("new max level: %s" % max_level)
            dynamic_silence = min_level
            print("peak to trough: %s" % (max_level - min_level))
        
        except Exception as e:
            raise("All Hell no... %s" % e)


def getmillis():
    return int(round(time.time() * 1000))


# returns the worked samples, scrols the data array
def get_sample():
    start = getmillis()
    frames = []
    sampling = False

    while audio_buffer:
        newchunk = audio_buffer.pop()
        #frames.append(np.frombuffer(newchunk, dtype=np.int16))
        
        if not sampling and np.amin(np.frombuffer(newchunk, dtype=np.int16)) < dynamic_silence:
            print("new sample, max: %s, min: %s, dynamic_silence: %s" % (np.amax(np.frombuffer(newchunk, dtype=np.int16)), np.amin(np.frombuffer(newchunk, dtype=np.int16)), dynamic_silence))
            frames.append(np.frombuffer(newchunk, dtype=np.int16))
            sampling = True
        elif sampling and np.amin(np.frombuffer(newchunk, dtype=np.int16)) < dynamic_silence:
            print("cont. sampling, max: %s, min: %s" % (np.amax(np.frombuffer(newchunk, dtype=np.int16)), np.amin(np.frombuffer(newchunk, dtype=np.int16))))
            frames.append(np.frombuffer(newchunk, dtype=np.int16))
        elif sampling and np.amin(np.frombuffer(newchunk, dtype=np.int16)) > dynamic_silence:
            print("finalizing sample, max: %s, min: %s, dynamic_silence: %s" % (np.amax(np.frombuffer(newchunk, dtype=np.int16)), np.amin(np.frombuffer(newchunk, dtype=np.int16)), dynamic_silence))
            frames.append(np.frombuffer(newchunk, dtype=np.int16))
            break
        else:
            print("idle, max: %s, min: %s, dynamic_silence: %s" % (np.amax(np.frombuffer(newchunk, dtype=np.int16)), np.amin(np.frombuffer(newchunk, dtype=np.int16)), dynamic_silence))
            frames.append(np.frombuffer(newchunk, dtype=np.int16))
            #break

        #if sampling and getmillis() - start > 2000:
        #    print("timeout: %s" % (getmillis() - start))
        #    frames.append(np.fromstring(newchunk, dtype=np.float32))
        #    break
        #else:
        #    frames.append(np.fromstring(newchunk, dtype=np.float32))

    #print("peak scan took: %s" % (getmillis()-start))

    global y, data
    if frames:
        start = getmillis()
        
        if frames:
            data = np.hstack(frames)
            data = np.hstack((data, y))
            data = data[:10000]
        else:
            pass

        end1 = getmillis()
    else:
        print("no frames")
    

    print(data)

    return data, rate


def monitorAudio(threadname):
    global y, sr, frequencies, times, spectrogram
    while 1:
        try:
            y, sr = get_sample()
            frequencies, times, spectrogram = signal.spectrogram(y, sr)
        except Exception as e:
            print("error %s" % e)
            raise Exception("crash: %s" % e)


def update_fig(n):
    global y, sr, im, plt, frequencies, times, spectrogram
    zmin = spectrogram.min()
    zmax = spectrogram.max()
    try:
        plt.pcolormesh(times, frequencies, spectrogram, cmap='RdBu', norm=LogNorm(vmin=zmin, vmax=zmax))
    except Exception as e:
        print("error updating chart")
        raise(e)

thread0 = Thread(target=audio_monitor, args=("audio_monitor-0",))
thread0.daemon=True
thread0.start()

time.sleep(1)

fig = plt.figure(figsize=(7, 7))
y, sr = get_sample()

thread1 = Thread(target=monitorAudio, args=("MonitorAudio-1",))
thread1.daemon = True
thread1.start()

frequencies, times, spectrogram = signal.spectrogram(y, sr)
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')

plt.tight_layout()

anim = animation.FuncAnimation(fig, update_fig, interval=25)

try:
    plt.show()
except:
    print("Plot Closed")

############### Terminate ###############

print("Program Terminated")