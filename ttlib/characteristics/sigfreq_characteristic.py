'''
Created on Jun 30, 2016

@author: jivan
'''
from __future__ import print_function
from ttlib.characteristics.generator_base import CharacteristicGenerator
# from analytics.models import Characteristic
from io import StringIO
import scipy.io.wavfile
from numpy import abs, fft
import sys

class SigFreq8(CharacteristicGenerator):
    version = '0.0.0'
    name = 'sigfreq8'
    dependencies = []

    charversion = '0.0'
    # Eliminate values less than this times the maximum fft coefficient
    cutoff_proportion = 0.1

    @classmethod
    def calculate(cls, wave_data, sample_rate):
        sigfreqs = {}

        # Split the data into 8 equal pieces
        split_indices = [ int(len(wave_data) / 8.0 * i) for i in range(0, 9)]
        wave_data_by_segment = [
            wave_data[split_indices[i - 1]:split_indices[i]] for i in range(1, 9)
        ]
        bucket_width = 10
        frequency_data_by_segment = [
            cls.get_frequency_spectrum(
                wave_data_by_segment[i], sample_rate, bucket_width=bucket_width
            )
            for i in range(8)
        ]

        for segment in range(8):
            freq_weights_1500 = []
            freqs_1500 = []
            freq_weights_3000 = []
            freqs_3000 = []

            for bucket in range(len(frequency_data_by_segment[segment])):
                freq = bucket * bucket_width - (bucket_width / 2)
                if freq >= 0 and freq < 1500:
                    freq_weights_1500.append(frequency_data_by_segment[segment][bucket])
                    freqs_1500.append(freq)
                elif freq >= 1500 and freq < 3000:
                    freq_weights_3000.append(frequency_data_by_segment[segment][bucket])
                    freqs_3000.append(freq)

            # Eliminate measurements less than half the maximum
            weight_cutoff_1500 = max(freq_weights_1500) * cls.cutoff_proportion
            filtered_weights_1500 = []
            filtered_freqs_1500 = []
            for weight, freq in zip(freq_weights_1500, freqs_1500):
                if weight >= weight_cutoff_1500:
                    filtered_weights_1500.append(weight)
                    filtered_freqs_1500.append(freq)

            weight_cutoff_3000 = max(freq_weights_3000) * cls.cutoff_proportion
            filtered_weights_3000 = []
            filtered_freqs_3000 = []
            for weight, freq in zip(freq_weights_3000, freqs_3000):
                if weight >= weight_cutoff_3000:
                    filtered_weights_3000.append(weight)
                    filtered_freqs_3000.append(freq)

            wa1500 = sum([ freq * weight for freq, weight in zip(filtered_freqs_1500, filtered_weights_1500) ]) \
                        / sum(filtered_weights_1500)
            wa3000 = sum([ freq * weight for freq, weight in zip(filtered_freqs_3000, filtered_weights_3000) ]) \
                        / sum(filtered_weights_3000)

            sigfreqs['sigfreq12-{}8'.format(segment + 1)] = wa1500
            sigfreqs['sigfreq22-{}8'.format(segment + 1)] = wa3000

        return sigfreqs

    @classmethod
    def calculate_bulk(cls, rss):
        """ Generates a weighted average of frequencies, ignoring frequencies with a coefficient
            less than cls.cutoff_proportion of the maximum fft coefficient.
        """
        # Values less than this times the maximum will be ignored
        charnames = [ 'sigfreq{}2-{}8'.format(a, b) for a in [1, 2] for b in range(1, 9) ]
        Characteristic.objects.filter(name__in=charnames)\
            .exclude(version=cls.charversion).delete()
        already_calculated = [ (c.recording.id, c.name) for c in
            Characteristic.objects.filter(name__in=charnames, version=cls.charversion)
        ]

        print('Generating significant frequency values for {} syllables'.format(rss.count()))
        new_characteristics = []
        for rs in rss:
            # Get the wave data for this syllable
            sio = StringIO(rs.content_as_silence_stripped_wav)
            sampling_rate, wave_data = scipy.io.wavfile.read(sio)

            # Split the data into 8 equal pieces
            split_indices = [ int(len(wave_data) / 8.0 * i) for i in range(0, 9)]
            wave_data_by_segment = [
                wave_data[split_indices[i - 1]:split_indices[i]] for i in range(1, 9)
            ]
            bucket_width = 10
            frequency_data_by_segment = [
                cls.get_frequency_spectrum(
                    wave_data_by_segment[i], sampling_rate, bucket_width=bucket_width
                )
                for i in range(8)
            ]

            for segment in range(8):
                n1 = 'sigfreq12-{}8'.format(segment + 1)
                n2 = 'sigfreq22-{}8'.format(segment + 1)
                if (rs.id, n1) in already_calculated and (rs.id, n2) in already_calculated:
                    continue

                freq_weights_1500 = []
                freqs_1500 = []
                freq_weights_3000 = []
                freqs_3000 = []

                for bucket in range(len(frequency_data_by_segment[segment])):
                    freq = bucket * bucket_width - (bucket_width / 2)
                    if freq >= 0 and freq < 1500:
                        freq_weights_1500.append(frequency_data_by_segment[segment][bucket])
                        freqs_1500.append(freq)
                    elif freq >= 1500 and freq < 3000:
                        freq_weights_3000.append(frequency_data_by_segment[segment][bucket])
                        freqs_3000.append(freq)

                # Eliminate measurements less than half the maximum
                weight_cutoff_1500 = max(freq_weights_1500) * cls.cutoff_proportion
                filtered_weights_1500 = []
                filtered_freqs_1500 = []
                for weight, freq in zip(freq_weights_1500, freqs_1500):
                    if weight >= weight_cutoff_1500:
                        filtered_weights_1500.append(weight)
                        filtered_freqs_1500.append(freq)

                weight_cutoff_3000 = max(freq_weights_3000) * cls.cutoff_proportion
                filtered_weights_3000 = []
                filtered_freqs_3000 = []
                for weight, freq in zip(freq_weights_3000, freqs_3000):
                    if weight >= weight_cutoff_3000:
                        filtered_weights_3000.append(weight)
                        filtered_freqs_3000.append(freq)

                wa1500 = sum([ freq * weight for freq, weight in zip(filtered_freqs_1500, filtered_weights_1500) ]) \
                            / sum(filtered_weights_1500)
                wa3000 = sum([ freq * weight for freq, weight in zip(filtered_freqs_3000, filtered_weights_3000) ]) \
                            / sum(filtered_weights_3000)

                c1 = Characteristic(
                        name='sigfreq12-{}8'.format(segment + 1), value=wa1500, recording=rs)
                c2 = Characteristic(
                        name='sigfreq22-{}8'.format(segment + 1), value=wa3000, recording=rs)
                new_characteristics.extend([c1, c2])
            print('.', end='')
            sys.stdout.flush()

        Characteristic.objects.bulk_create(new_characteristics)
        print('done')

    @classmethod
    def get_frequency_spectrum(cls, wave_data, sampling_rate, bucket_width=10, min_freq=150, max_freq=8000):
        ''' Returns a list with each element the fourier coefficient for that frequency,
                ie. spectrum[4] would return an integer representing the contribution of
                a 4Hz signal to *wave_data*
            wave_data is a numpy array containing PCM encoded sound data.
        '''
        duration = len(wave_data) / float(sampling_rate)
#         cprint('rate: {}, len(data): {}, duration: {}s'.format(sampling_rate, len(wave_data), duration))
        freq_amplitudes = abs(fft.fft(wave_data))
        # Due to symmetry of fft transform on signal, only consider half of result.
        candidate_amplitudes = freq_amplitudes[:len(freq_amplitudes + 1) / 2]

        # One sample is 1/duration Hz wide
        frequency_spectrum = [ 0 ] * (int(len(candidate_amplitudes) / duration / bucket_width) + 1)
        for i, coef in enumerate(candidate_amplitudes):
            # Frequency Bucket
            freq = i / duration
            if freq < min_freq or freq > max_freq: continue

            fb = int(i / duration / bucket_width)
            frequency_spectrum[fb] += coef
    #     frequency_spectrum = candidate_amplitudes
        return frequency_spectrum
