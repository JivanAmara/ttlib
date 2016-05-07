'''
Created on May 7, 2016

@author: jivan
'''
from __future__ import print_function
import argparse
import sys
import numpy
import scipy.io.wavfile
from analyze import get_frequency_with_peak_amplitude

def plot_frequency_spectrum(wave_file):
    ''' Opens a window graphing the frequency spectrum of *wave_file*.
        *wave_file* is an open file-like object
    '''
    import matplotlib.pyplot as plt

    rate, data = scipy.io.wavfile.read(wave_file)
    duration = len(data) / float(rate)
    freq_amplitudes = numpy.abs(numpy.fft.fft(data))

    # Half of values, rounding up if odd.  Use this due to the symmetrical nature of fft on a signal.
    half_count = (len(freq_amplitudes) + 1) / 2

    # Make x-axis labels as frequency value
    k = numpy.arange(half_count)
    frqLabel = k / duration

    # Eliminate values outside 85Hz - 8kHz, as this is the effective limit of frequencies in human speach.
    # Perhaps we should consider a limit of 300Hz - 3400Hz as this is the telephony band.
    max_freq = 8000
    min_freq = 85
    max_freq_index = numpy.min(numpy.where(frqLabel == max_freq + 1))
    min_freq_index = numpy.min(numpy.where(frqLabel == min_freq))
    max_index = min(max_freq_index, half_count)
    min_index = max(0, min_freq_index)
    plt.plot(frqLabel[min_index:max_index], freq_amplitudes[min_index:max_index])

    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Frequency coefficients from fft')
    plt.title('Frequency Spectrum')
    plt.grid(True)
#     plt.savefig("test.png")
    plt.show()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('wavefile', help='Name of wavefile to get frequencies for')
    subparsers = p.add_subparsers()
    peak_freq_parser = subparsers.add_parser('peak-freq', help='Show frequency with peak amplitude in file.')
    peak_freq_parser.set_defaults(command='peak-freq')
    plot_freq_parser = subparsers.add_parser('plot-freq', help='Plot the frequency spectrum in the file.')
    plot_freq_parser.set_defaults(command='plot-freq')
    args = p.parse_args()

    if args.command == 'peak-freq':
        with open(args.wavefile) as wf:
            freq = get_frequency_with_peak_amplitude(wf)
            print('Peak at {}Hz'.format(freq))
    elif args.command == 'plot-freq':
        with open(args.wavefile) as wf:
            plot_frequency_spectrum(wf)
    else:
        raise Exception('Unexpected subcommand in args: {}'.format(' '.join(sys.argv)))
