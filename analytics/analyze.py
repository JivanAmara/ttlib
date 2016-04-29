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
from scipy.io import wavfile


# Full path to the directory containing this file.
DIRPATH = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))

def calculate_peak_frequency_all():
    rss = RecordedSyllable.objects.all()
    MinFreq11.objects.all().delete()
    MaxFreq11.objects.all().delete()
    new_attributes_min = []
    new_attributes_max = []
    for i, rs in enumerate(rss):
        if rs.content_as_wav is None:
            print('no wav...skipping')
            continue

        sio = StringIO(rs.content_as_wav)
        try:
            rate, data = wavfile.read(sio)
        except ValueError as ex:
            if ex.message == 'Unknown wave file format':
                print('Unable to read wav format for {}: {}'.format(rs.user.username, rs.syllable))
                continue

        sio.close()
        freqs = numpy.fft.rfft(data)
        min_index, min_freq = min(enumerate(freqs), key=lambda x: x[1])
        max_index, max_freq = max(enumerate(freqs), key=lambda x: x[1])
        minf = MinFreq11(recording=rs, attr=min_index)
        maxf = MaxFreq11(recording=rs, attr=max_index)
        new_attributes_min.append(minf)
        new_attributes_max.append(maxf)
        print('{}Hz, [{}, {}]'.format(rate, min(freqs), max(freqs)))
    print('...out of {} recorded syllables'.format(i))
    print('Saving new attributes...', end='')
    MinFreq11.objects.bulk_create(new_attributes_min)
    MaxFreq11.objects.bulk_create(new_attributes_max)
    print('done')

def graph_attribute(attribute_name):
    attribute_name = attribute_name.lower()
    model_lookup = {
        'minfreq11': MinFreq11,
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
    from analytics.models import MinFreq11, MaxFreq11

    if args.subcommand == 'frequency':
        calculate_peak_frequency_all()
    elif args.subcommand == 'graph':
        graph_attribute(args.attribute)
    else:
        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)
