'''
Created on Apr 21, 2016

@author: jivan
'''
from __future__ import print_function

from cStringIO import StringIO
import argparse
import os, sys

import django
import numpy
import scipy.io.wavfile


# Full path to the directory containing this file.
DIRPATH = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))

OUTPUT = False
def cprint(*args, **kwargs):
    ''' Conditional print, if OUTPUT==True, print, otherwise ignore.
    '''
    if OUTPUT:
        print(*args, **kwargs)

def get_frequency_with_peak_amplitude(wave_file):
    ''' Returns the frequency (Hz) at the peak amplitude of a fourier transform.  This is essentially the most-used
        frequency in *wave_file*.
        wave_file is an open file-like object
    '''
    rate, data = scipy.io.wavfile.read(wave_file)
    duration = len(data) / float(rate)
    cprint('rate: {}, len(data): {}, duration: {}s'.format(rate, len(data), duration))
    cprint('data[:10]: {}'.format(data))
    freq_amplitudes = numpy.abs(numpy.fft.fft(data))
    max_freq_amplitude = numpy.max(freq_amplitudes[:len(freq_amplitudes) / 2])
    index_with_max_amplitude = numpy.argmax(freq_amplitudes[:len(freq_amplitudes) / 2])
    freq_with_max_amplitude = index_with_max_amplitude / duration
    cprint('len(feq_amplitudes): {}'.format(len(freq_amplitudes)))
    cprint('max freq amplitude: {}'.format(max_freq_amplitude))
    cprint('index of max freq amplitude: {}'.format(index_with_max_amplitude))
    cprint('freq @max amplitude: {}'.format(freq_with_max_amplitude))
    return freq_with_max_amplitude

def calculate_peak_frequency_all():
    rss = RecordedSyllable.objects.all()
    print('Calculating peak amplitude frequency for {} RecordedSyllables'.format(rss.count()))
    MaxFreq11.objects.all().delete()
    new_attributes_max = []
    for rs in rss:
        if rs.content_as_wav is None:
            print('no wav...skipping')
            continue

        sio = StringIO(rs.content_as_wav)
        try:
            peak_freq = get_frequency_with_peak_amplitude(sio)
            print('.', end='')
            sys.stdout.flush()
        except ValueError as ex:
            if ex.message == 'Unknown wave file format':
                print('x', end='')
                sys.stdout.flush()
                continue
            else:
                raise

        maxf = MaxFreq11(recording=rs, attr=peak_freq)
        new_attributes_max.append(maxf)
    print('Saving {} new attributes for {} samples...'.format(len(new_attributes_max), rss.count()), end='')
    MaxFreq11.objects.bulk_create(new_attributes_max)
    print('done')

def graph_attribute(attribute_name):
    attribute_name = attribute_name.lower()
    model_lookup = {
        'maxfreq11': MaxFreq11,
    }
    AttrModel = model_lookup[attribute_name]
    for tone in range(1, 6):
        data = [ o.attr for o in AttrModel.objects.filter(recording__syllable__tone=tone) ]
        import matplotlib.pyplot as plt

        # X-Axis as frequency
        s = numpy.arange(0.0, len(data), 1)
        plt.subplot(1, 5, tone)
        plt.plot(s, data)

        plt.xlabel('frequency')
        plt.ylabel('preponderance')
        plt.title('{} - Tone {}'.format(attribute_name, tone))
        plt.grid(True)
    #     plt.savefig("test.png")
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    analyze_parser = subparsers.add_parser('frequency', help='Determine peak frequency for each recorded syllable')
    analyze_parser.set_defaults(subcommand='frequency')
    graph_parser = subparsers.add_parser('graph', help='Graph an attribute by tone')
    graph_parser.set_defaults(subcommand='graph')
    graph_parser.add_argument('attribute', type=str, help='Attribute to graph')
    migrate_parser = subparsers.add_parser('migrate', help='Perform a Django model migration')
    migrate_parser.set_defaults(subcommand='migrate')
    makemigrations_parser = subparsers.add_parser('makemigrations', help='Auto-create Django model migration')
    makemigrations_parser.set_defaults(subcommand='makemigrations')

    args = parser.parse_args()

    sys.path.append(DIRPATH)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'script_settings'
    django.setup()
    from tonerecorder.models import RecordedSyllable
    from analytics.models import MaxFreq11

    if args.subcommand == 'frequency':
        calculate_peak_frequency_all()
    elif args.subcommand == 'graph':
        graph_attribute(args.attribute)
    else:
        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)
