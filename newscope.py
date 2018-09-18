from threading import Thread

import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import struct
import pyaudio
from scipy.fftpack import fft
from sklearn import preprocessing
from scipy import signal
import sys
import time

data_frames = []


class AudioStream(object):
    def __init__(self):

        # pyqtgraph stuff
        pg.setConfigOptions(antialias=False)
        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.win = pg.GraphicsWindow(title='Spectrum Analyzer')
        self.win.setWindowTitle('Spectrum Analyzer')
        self.win.setGeometry(5, 115, 1024, 1070)

        wf_xlabels = [(0, '0'), (2048, '2048'), (4096, '4096')]
        wf_xaxis = pg.AxisItem(orientation='bottom')
        wf_xaxis.setTicks([wf_xlabels])

        wf_ylabels = [(-16384, '-16384'), (0, '0'), (16384, '16384')]
        wf_yaxis = pg.AxisItem(orientation='left')
        wf_yaxis.setTicks([wf_ylabels])

        sp_xlabels = [
            (np.log10(10), '10'), (np.log10(100), '100'),
            (np.log10(1000), '1000'), (np.log10(22050), '22050')
        ]

        sp_xaxis = pg.AxisItem(orientation='bottom')
        sp_xaxis.setTicks([sp_xlabels])

        self.waveform = self.win.addPlot(
            title='WAVEFORM', row=1, col=1, axisItems={'bottom': wf_xaxis, 'left': wf_yaxis},
        )
        self.spectrum = self.win.addPlot(
            title='SPECTRUM', row=2, col=1, axisItems={'bottom': sp_xaxis},
        )

        self.amplitude = self.win.addPlot(
            title='AMPLITUDE', row=3, col=1,
        )

        # pyaudio stuff
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024 * 2

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )
        # waveform and spectrum x points
        self.x = np.arange(0, 2 * self.CHUNK, 2)
        self.f = np.linspace(0, self.RATE / 2, self.CHUNK / 2)

        self.data = []
        self.sampleing = False

        self.thread0 = Thread(target=self.monitor, args=("audio_monitor-0",))
        self.thread0.daemon = True
        self.thread0.start()

    def monitor(self, threadname):
        while True:
            newchunk = self.stream.read(self.CHUNK, exception_on_overflow=False)
            print("min:%s, max:%s" % (np.amin(np.frombuffer(newchunk, dtype=np.int16)), np.amax(np.frombuffer(newchunk, dtype=np.int16))))
            if np.amin(np.frombuffer(newchunk, dtype=np.int16)) > 0:
                self.sampling = True
                print("Starting sample")
                self.data.append(np.frombuffer(newchunk, dtype=np.int16))

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def set_plotdata(self, name, data_x, data_y):
        if name in self.traces:
            self.traces[name].setData(data_x, data_y)
        else:
            if name == 'waveform':
                self.traces[name] = self.waveform.plot(pen='c', width=3)
                # self.waveform.setYRange(0, 255, padding=0)
                self.waveform.setXRange(0, 2 * self.CHUNK, padding=0.005)
            if name == 'spectrum':
                self.traces[name] = self.spectrum.plot(pen='m', width=3)
                self.spectrum.setLogMode(x=True, y=True)
                #self.spectrum.setYRange(-1, 200, padding=1)
                self.spectrum.setXRange(np.log10(10), np.log10(self.RATE / 2), padding=0.005)
            if name == 'amplitude':
                self.traces[name] = self.amplitude.plot(np.random.rand(1024), pen='y')

    def update(self):
        wf_data = self.stream.read(self.CHUNK, exception_on_overflow=False)
        wf_data = np.frombuffer(wf_data, dtype=np.int16)
        self.set_plotdata(name='waveform', data_x=self.x, data_y=wf_data, )
        sp_data = fft(np.array(wf_data, dtype=np.int16))
        sp_data = np.abs(sp_data[0:int(self.CHUNK / 2)]) * 2 / (wf_data.max() * self.CHUNK)
        print("sp_data: %s" % sp_data)
        # binarized_peaks = preprocessing.Binarizer(threshold=2.4,).transform(sp_data)
        binarized_peaks = np.where(sp_data>0.1, 20000, 1)
        print("binarized_peaks: %s" % binarized_peaks)
        self.set_plotdata(name='spectrum', data_x=self.f, data_y=binarized_peaks)
        self.set_plotdata(name='amplitude', data_x=self.x, data_y=np.abs(wf_data))

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(20)
        self.start()


if __name__ == '__main__':
    audio_app = AudioStream()
    audio_app.animation()
