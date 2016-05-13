'''
Created on Apr 21, 2016

@author: jivan
'''
from __future__ import print_function

import argparse
from cStringIO import StringIO
from collections import defaultdict
import os, sys
import itertools
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

def get_frequency_with_peak_amplitude(wave_data, sampling_rate, min_freq=150, max_freq=8000):
    ''' Returns the frequency (Hz) at the peak amplitude of a fourier transform.  This is the most-used
        frequency in *wave_data*.
        wave_data is a numpy array containing PCM encoded sound data.
    '''
    duration = len(wave_data) / float(sampling_rate)
    cprint('rate: {}, len(data): {}, duration: {}s'.format(sampling_rate, len(wave_data), duration))
    freq_amplitudes = numpy.abs(numpy.fft.fft(wave_data))
    # Due to symmetry of fft transform on signal, only consider half of result.
    candidate_amplitudes = freq_amplitudes[:len(freq_amplitudes + 1) / 2]
    # Zero-out frequencies below min or above max so they aren't considered.
    while True:
        max_freq_amplitude = numpy.max(candidate_amplitudes)
        index_with_max_amplitude = numpy.argmax(candidate_amplitudes)
        freq_with_max_amplitude = index_with_max_amplitude / duration
        if freq_with_max_amplitude >= min_freq and freq_with_max_amplitude <= max_freq:
            break
        candidate_amplitudes[index_with_max_amplitude] = 0

    cprint('len(feq_amplitudes): {}'.format(len(freq_amplitudes)))
    cprint('max freq amplitude: {}'.format(max_freq_amplitude))
    cprint('index of max freq amplitude: {}'.format(index_with_max_amplitude))
    cprint('freq @max amplitude: {}'.format(freq_with_max_amplitude))
    return freq_with_max_amplitude

def calculate_8_segment_peak_frequency_all():
    rss = RecordedSyllable.objects.all()
    print('Calculating 8-segment peak amplitude frequency for {} RecordedSyllables'.format(rss.count()))
    PeakFreq18.objects.all().delete()
    PeakFreq28.objects.all().delete()
    PeakFreq38.objects.all().delete()
    PeakFreq48.objects.all().delete()
    PeakFreq58.objects.all().delete()
    PeakFreq68.objects.all().delete()
    PeakFreq78.objects.all().delete()
    PeakFreq88.objects.all().delete()

    new_attributes = defaultdict(list)
    missing_wav_count = 0
    for rs in rss:
        if rs.content_as_silence_stripped_wav is None:
            print('no wav...skipping')
            missing_wav_count += 1
            continue

        sio = StringIO(rs.content_as_silence_stripped_wav)

        try:
            sample_rate, wave_data = scipy.io.wavfile.read(sio)
        except ValueError as ex:
            if ex.message == 'Unknown wave file format':
                print('x', end='')
                sys.stdout.flush()
                continue
            else:
                raise

        sample_count = len(wave_data)
        segment_ends = [ (sample_count * i / 8) for i in range(0, 9) ]
        if segment_ends[-1] != sample_count:
            msg = 'segmentation logic faulty, {} != {}'.format(segment_ends[-1], sample_count)
            raise Exception(msg)

        peak_freqs = [
            get_frequency_with_peak_amplitude(
                wave_data[segment_ends[i - 1]:segment_ends[i]], sample_rate
            ) for i in range(1, 9)
        ]
        print('.', end='')
        sys.stdout.flush()

        model_classes = {
            1: PeakFreq18,
            2: PeakFreq28,
            3: PeakFreq38,
            4: PeakFreq48,
            5: PeakFreq58,
            6: PeakFreq68,
            7: PeakFreq78,
            8: PeakFreq88,
        }
        for i in range(1, 9):
            ModelClass = model_classes[i]
            pf_instance = ModelClass(recording=rs, attr=peak_freqs[i - 1])
            new_attributes[i].append(pf_instance)

    print('Saving {} new attributes for {} samples segmented into 8 pieces each...'\
              .format(len(new_attributes), rss.count()), end='')
    for i in range(1, 9):
        ModelClass = model_classes[i]
        ModelClass.objects.bulk_create(new_attributes[i])

    print('{} RecordedSyllable instances missing content_as_silence_stripped_wav'\
              .format(missing_wav_count)
    )
    print('done')

def calculate_8_segment_peak_frequency_change_all():
    rss = RecordedSyllable.objects.all().select_related('peakfreqchange28', 'peakfreqchange38'
                , 'peakfreqchange48', 'peakfreqchange58', 'peakfreqchange68', 'peakfreqchange78')

    print('Calculating 8-segment peak frequency changes for {} RecordedSyllables'.format(rss.count()))
    PeakFreqChange28.objects.all().delete()
    PeakFreqChange38.objects.all().delete()
    PeakFreqChange48.objects.all().delete()
    PeakFreqChange58.objects.all().delete()
    PeakFreqChange68.objects.all().delete()
    PeakFreqChange78.objects.all().delete()
    PeakFreqChange88.objects.all().delete()

    new_attributes = defaultdict(list)
    for rs in rss:
        model_classes = [
            ['peakfreq18', 'peakfreq28', PeakFreqChange28],
            ['peakfreq28', 'peakfreq38', PeakFreqChange38],
            ['peakfreq38', 'peakfreq48', PeakFreqChange48],
            ['peakfreq48', 'peakfreq58', PeakFreqChange58],
            ['peakfreq58', 'peakfreq68', PeakFreqChange68],
            ['peakfreq68', 'peakfreq78', PeakFreqChange78],
            ['peakfreq78', 'peakfreq88', PeakFreqChange88],
        ]
        for attr1_field, attr2_field, PFC in model_classes:
            try:
                attr2 = getattr(rs, attr2_field).attr
                attr1 = getattr(rs, attr1_field).attr
            except Exception as ex:
                print('x', end='')
                sys.stdout.flush()
                continue

            freq_change = attr2 - attr1
            pfc = PFC(recording=rs, attr=freq_change)
            new_attributes[PFC].append(pfc)
            print('.', end='')
            sys.stdout.flush()

    print('Saving {} new attributes for {} samples...'\
              .format(len(list(itertools.chain.from_iterable(new_attributes.values()))), rss.count()), end='')
    for PeakFreqModel, new_instance_list in new_attributes.items():
        PeakFreqModel.objects.bulk_create(new_instance_list)

    print('done')


def graph_attribute(attribute_name):
    attribute_name = attribute_name.lower()
    model_lookup = {
        'maxfreq11': MaxFreq11,
        'peakfreq18': PeakFreq18,
        'peakfreq28': PeakFreq28,
        'peakfreq38': PeakFreq38,
        'peakfreq48': PeakFreq48,
        'peakfreq58': PeakFreq58,
        'peakfreq68': PeakFreq68,
        'peakfreq78': PeakFreq78,
        'peakfreq88': PeakFreq88,
        'peakfreqchange28': PeakFreqChange28,
        'peakfreqchange38': PeakFreqChange38,
        'peakfreqchange48': PeakFreqChange48,
        'peakfreqchange58': PeakFreqChange58,
        'peakfreqchange68': PeakFreqChange68,
        'peakfreqchange78': PeakFreqChange78,
        'peakfreqchange88': PeakFreqChange88,
    }
    AttrModel = model_lookup[attribute_name]
    initial_subplot = None
    for tone in range(1, 6):
        data = [ o.attr for o in AttrModel.objects.filter(
                                  recording__syllable__tone=tone, recording__syllable__sound='ba')
        ]
        import matplotlib.pyplot as plt

        if tone == 1:
            initial_subplot = plt.subplot(1, 5, tone)
        else:
            plt.subplot(1, 5, tone, sharey=initial_subplot)

        min_value, max_value, bin_width = (-100, 100, 10)
        plt.hist(data, range(min_value, max_value, bin_width))

        plt.xlabel('attr')
        plt.ylabel('count')
        plt.title('{} - Tone {}'.format(attribute_name, tone))
        plt.grid(True)
    #     plt.savefig("test.png")
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    freq8_parser = subparsers.add_parser('frequency8', help='Determine peak frequency for each 1/8th of each recorded syllable ')
    freq8_parser.set_defaults(subcommand='frequency8')
    freqchange8_parser = subparsers.add_parser('freqchange8', help='Determine peak frequency for each 1/8th of each recorded syllable ')
    freqchange8_parser.set_defaults(subcommand='freqchange8')
    graph_parser = subparsers.add_parser('graph', help='Graph an attribute by tone')
    graph_parser.set_defaults(subcommand='graph')
    graph_parser.add_argument('attribute', type=str, help='Attribute to graph')
    migrate_parser = subparsers.add_parser('migrate', help='Perform a Django model migration')
    migrate_parser.set_defaults(subcommand='migrate')
    makemigrations_parser = subparsers.add_parser('makemigrations', help='Auto-create Django model migration')
    makemigrations_parser.set_defaults(subcommand='makemigrations')

    args = parser.parse_args()

    sys.path.append(DIRPATH)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'analytics.script_settings'
    django.setup()
    from tonerecorder.models import RecordedSyllable
    from analytics.models import MaxFreq11\
        , PeakFreq18, PeakFreq28, PeakFreq38, PeakFreq48 \
        , PeakFreq58, PeakFreq68, PeakFreq78, PeakFreq88 \
        , PeakFreqChange28, PeakFreqChange38, PeakFreqChange48 \
        , PeakFreqChange58, PeakFreqChange68, PeakFreqChange78, PeakFreqChange88
    if args.subcommand == 'frequency8':
        calculate_8_segment_peak_frequency_all()
    elif args.subcommand == 'freqchange8':
        calculate_8_segment_peak_frequency_change_all()
    elif args.subcommand == 'graph':
        graph_attribute(args.attribute)
    else:
        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)
