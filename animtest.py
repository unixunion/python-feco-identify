import pyaudio
import numpy as np
import time

import sys
from matplotlib import pyplot as plt, animation
from threading import Thread

from scipy.fftpack import fft

CHUNKSIZE = 256  # fixed chunk size
SILENCE = 2000

# initialize portaudio
p = pyaudio.PyAudio()

print("audio device")
print(p.get_default_input_device_info())


hz = int(p.get_default_input_device_info()['defaultSampleRate'])

stream = p.open(format=pyaudio.paInt16, channels=1, rate=hz, input=True, frames_per_buffer=CHUNKSIZE)

data = None
numpydata = np.zeros(CHUNKSIZE)

lastframe = numpydata

n = numpydata.size
timestep = 0.1
x = np.fft.fftfreq(n, d=timestep)


def getmillis():
    """
    get current time in millis
    :return: 
    """
    return int(round(time.time() * 1000))


def monitor(threadname):
    global numpydata
    global sampled;
    while 1:
        try:
            print("sampling")
            stream.start_stream()
            start = getmillis()
            data = stream.read(CHUNKSIZE)
            end1 = getmillis()
            stream.stop_stream()
            numpydata = np.fromstring(data, dtype=np.int16)
            # print("sample time: %s" % (end1 - start))
            # print("numpy commit: %s" % (getmillis() - end1))

        except Exception, e:
            print("error %s" % e)
            raise Exception("Crash")


def graph(threadname):
    global plt
    while 1:
        if np.amax(numpydata) > SILENCE or np.amin(numpydata) < -1 * SILENCE:
            plt.pause(0.01)
        time.sleep(1)


if __name__ == "__main__":

    try:

        thread1 = Thread(target=monitor, args=("Monitor-1",))
        thread2 = Thread(target=graph, args=("Plot-1",))

        thread1.daemon = True
        thread2.daemon = True

        thread1.start()
        thread2.start()

        # plt.ion()
        fig, ax = plt.subplots()

        # line, = ax.plot(x, numpydata[:CHUNKSIZE/2-1])
        line, = ax.plot(x, numpydata)


        def animate(i):

            if np.amax(numpydata) > SILENCE or np.amin(numpydata) < -1*SILENCE:
                # plt.ylim(ymax=np.amax(numpydata))
                # # plt.ylim(ymax=2048)
                # plt.ylim(ymin=np.amin(numpydata))
                # plt.ylim(ymin=-2048)
                # line.set_ydata(numpydata)  # update the data

                # b = [(ele / 2 ** 8.) * 2 - 1 for ele in numpydata]
                # c = fft(b)
                # d = len(c) / 2

                # print("abs")
                # print(abs(c[:(d-1)]))

                # print("len")
                # print(len(abs(c[:(d-1)])))

                fourier = np.fft.fft(numpydata, norm="ortho")

                plt.ylim(ymax=np.amax(fourier)+1)
                # plt.ylim(ymax=2048)
                plt.ylim(ymin=np.amin(fourier)-1)
                # plt.legend()

                line.set_ydata(fourier)
                global lastframe
                lastframe=fourier
                # plt.draw()

                # line.set_ydata(abs(c[:(d-1)]))
            else:
                # print("silence")
                pass

            return line,


        def init():
            # line.set_ydata(np.ma.array(x, mask=True))
            print("resetting")
            line.set_ydata(lastframe) # update the data
            # k = np.arange(len(numpydata))
            # T = len(numpydata) / hz  # where fs is the sampling frequency
            # frqLabel = k / T
            # plt.xlabel = frqLabel
            return line,


        # line, = ax.plot(x, numpydata[:CHUNKSIZE/2-1])
        line, = ax.plot(x, numpydata)

        ani = animation.FuncAnimation(fig, animate, numpydata, init_func=init,
                                      interval=25, blit=True)

        plt.ylim(ymax=np.amax(numpydata))
        plt.show()


        while True:
            try:
                pass
            except KeyboardInterrupt, e:
                print "shutting down ..."
                sys.exit(1)


    except KeyboardInterrupt, e:
        print "cleaning up"
        stream.stop_stream()
        stream.close()
        p.terminate()
        sys.exit(1)

    except Exception, e:
        print ("exception: %s" % e)
        sys.exit(1)