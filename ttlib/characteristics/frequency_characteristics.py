'''
Created on Jun 30, 2016

@author: jivan
'''
from __future__ import print_function
from ttlib.characteristics.generator_base import CharacteristicGenerator
# from analytics.models import Characteristic
from io import StringIO
import scipy.io.wavfile
import sys
from numpy import abs, max, fft, argmax

cprint = lambda x: None

def get_frequency_with_peak_amplitude(wave_data, sampling_rate, min_freq=150, max_freq=8000):
    ''' Returns the frequency (Hz) at the peak amplitude of a fourier transform.  This is the most-used
        frequency in *wave_data*.
        wave_data is a numpy array containing PCM encoded sound data.
    '''
    duration = len(wave_data) / float(sampling_rate)
    cprint('rate: {}, len(data): {}, duration: {}s'.format(sampling_rate, len(wave_data), duration))
    freq_amplitudes = abs(fft.fft(wave_data))
    # Due to symmetry of fft transform on signal, only consider half of result.
    candidate_amplitudes = freq_amplitudes[:len(freq_amplitudes + 1) / 2]
    # Zero-out frequencies below min or above max so they aren't considered.
    while True:
        max_freq_amplitude = max(candidate_amplitudes)
        index_with_max_amplitude = argmax(candidate_amplitudes)
        freq_with_max_amplitude = index_with_max_amplitude / duration
        if freq_with_max_amplitude >= min_freq and freq_with_max_amplitude <= max_freq:
            break
        candidate_amplitudes[index_with_max_amplitude] = 0

    cprint('len(feq_amplitudes): {}'.format(len(freq_amplitudes)))
    cprint('max freq amplitude: {}'.format(max_freq_amplitude))
    cprint('index of max freq amplitude: {}'.format(index_with_max_amplitude))
    cprint('freq @max amplitude: {}'.format(freq_with_max_amplitude))
    return freq_with_max_amplitude

class MaxFreq8(CharacteristicGenerator):
    version = '0.0.0'
    dependencies = []
    name = 'maxfreq8'

    @classmethod
    def calculate(cls, wave_data, sample_rate):
        ''' *brief*: Calculates the max frequency characteristics for wave_data split into 8
                segments.
            *return*: Dictionary of the form {<characteristic_name>: <characteristic_value>, ...}
        '''
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

        charvalues = {
            'maxfreq{}8'.format(i): peak_freqs[i - 1] for i in range(1, 9)
        }

        return charvalues

    @classmethod
    def calculate_bulk(cls, rss):
        print('Calculating 8-segment peak fft coefficient frequency for {} RecordedSyllables'.format(rss.count()))
        characteristic_names = [ 'maxfreq{}8'.format(i) for i in range(1, 9) ]
        characteristic_names.append('maxfreq')
        Characteristic.objects.filter(name__in=characteristic_names).delete()

        new_characteristics = []
        missing_wav_count = 0
        for rs in rss:
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

            for i in range(1, 9):
                c = Characteristic(name='maxfreq{}8'.format(i), recording=rs, value=peak_freqs[i - 1])
                new_characteristics.append(c)

            print('.', end='')
            sys.stdout.flush()

        Characteristic.objects.bulk_create(new_characteristics)
        print('done')

class MaxFreqChange8(CharacteristicGenerator):
    version = '0.0.0'
    name = 'maxfreqchange8'
    dependencies = ['maxfreq8']

    @classmethod
    def calculate(cls, wave_data, sample_rate):
        freqchanges = {}
        maxfreqs = MaxFreq8.calculate(wave_data, sample_rate)
        for i in range(1, 8):
            first_charname = 'maxfreq{}8'.format(i)
            second_charname = 'maxfreq{}8'.format(i + 1)
            if first_charname not in maxfreqs or second_charname not in maxfreqs:
                continue

            freqchange = maxfreqs[second_charname] - maxfreqs[first_charname]
            freqchanges['freqchange{}{}8'.format(i, i + 1)] = freqchange

        return freqchanges

    @classmethod
    def calculate_bulk(cls, rss):
        print('Calculating 8-segment peak fft coefficient frequency change for {} RecordedSyllables'.format(rss.count()))
        new_characteristics = []
        characteristic_names = [ 'freqchange{}{}8'.format(i, i + 1) for i in (1, 8) ]
        Characteristic.objects.filter(name__in=characteristic_names).delete()

        for rs in rss:
            for i in range(1, 8):
                first_charname = 'maxfreq{}8'.format(i)
                second_charname = 'maxfreq{}8'.format(i + 1)
                try:
                    first_measure = Characteristic.objects.get(name=first_charname, recording=rs).value
                except Characteristic.DoesNotExist:
                    print('Couldn\'t find characteristic {} for RecordedSyllable w/ id: {}'\
                              .format(first_charname, rs.id))
                    continue
                try:
                    second_measure = Characteristic.objects.get(name=second_charname, recording=rs).value
                except Characteristic.DoesNotExist:
                    print('Couldn\'t find characteristic {} for RecordedSyllable w/ id: {}'\
                              .format(second_charname, rs.id))
                    continue

                freqchange = second_measure - first_measure
                c = Characteristic(
                    recording=rs, name='freqchange{}{}8'.format(i, i + 1), value=freqchange
                )
                new_characteristics.append(c)
            print('.', end='')
            sys.stdout.flush()
        Characteristic.objects.bulk_create(new_characteristics)
        print('done')
