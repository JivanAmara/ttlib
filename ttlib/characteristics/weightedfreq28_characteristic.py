'''
Created on Jun 30, 2016

@author: jivan
'''
from __future__ import print_function

from cStringIO import StringIO
import sys
from analytics.models import Characteristic
import scipy.io.wavfile
from analytics.characteristics.generator_base import CharacteristicGenerator
from analytics.characteristics.sigfreq_characteristic import SigFreq8
from logging import getLogger

logger = getLogger(__name__)

class WeightedFreq28(CharacteristicGenerator):

    @classmethod
    def calculate(cls, wave_data, sample_rate):
        weightedfreqs = {}

        # Split the data into 8 equal pieces
        split_indices = [ int(len(wave_data) / 8.0 * i) for i in range(0, 9)]
        wave_data_by_segment = [
            wave_data[split_indices[i - 1]:split_indices[i]] for i in range(1, 9)
        ]
        bucket_width = 10
        frequency_data_by_segment = [
            SigFreq8.get_frequency_spectrum(
                wave_data_by_segment[i], sample_rate, bucket_width=bucket_width
            ) for i in range(8)
        ]

        for segment in range(8):
            freqs1500 = []
            weights1500 = []
            freqs3000 = []
            weights3000 = []
            for bucket in range(len(frequency_data_by_segment[segment])):
                freq = bucket * bucket_width - (bucket_width / 2)
                if freq >= 0 and freq < 1500:
                    targetfreqs = freqs1500
                    targetweights = weights1500
                elif freq >= 1500 and freq < 3000:
                    targetfreqs = freqs3000
                    targetweights = weights3000
                else:
                    continue

                targetfreqs.append(bucket * bucket_width - (bucket_width / 2))
                targetweights.append(frequency_data_by_segment[segment][bucket])

            wa1500 = sum([ freq * weight for freq, weight in zip(freqs1500, weights1500) ]) \
                        / sum(weights1500)
            wa3000 = sum([ freq * weight for freq, weight in zip(freqs3000, weights3000) ]) \
                        / sum(weights3000)

            weightedfreqs['weightedfreq12-{}8'.format(segment + 1)] = wa1500
            weightedfreqs['weightedfreq22-{}8'.format(segment + 1)] = wa3000

        return weightedfreqs

    @classmethod
    def calculate_bulk(cls, rss):
        charnames = [ 'weightedfreq{}2-{}8'.format(a, b) for a in [1, 2] for b in range(1, 9) ]
        Characteristic.objects.filter(name__in=charnames).delete()

        print('Generating weighted frequency average for {} syllables'.format(rss.count()))
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
                SigFreq8.get_frequency_spectrum(
                    wave_data_by_segment[i], sampling_rate, bucket_width=bucket_width
                ) for i in range(8)
            ]

            for segment in range(8):
                freqs1500 = []
                weights1500 = []
                freqs3000 = []
                weights3000 = []
                for bucket in range(len(frequency_data_by_segment[segment])):
                    freq = bucket * bucket_width - (bucket_width / 2)
                    if freq >= 0 and freq < 1500:
                        targetfreqs = freqs1500
                        targetweights = weights1500
                    elif freq >= 1500 and freq < 3000:
                        targetfreqs = freqs3000
                        targetweights = weights3000
                    else:
                        continue

                    targetfreqs.append(bucket * bucket_width - (bucket_width / 2))
                    targetweights.append(frequency_data_by_segment[segment][bucket])

                wa1500 = sum([ freq * weight for freq, weight in zip(freqs1500, weights1500) ]) \
                            / sum(weights1500)
                wa3000 = sum([ freq * weight for freq, weight in zip(freqs3000, weights3000) ]) \
                            / sum(weights3000)

                c1 = Characteristic(
                        name='weightedfreq12-{}8'.format(segment + 1), value=wa1500, recording=rs)
                c2 = Characteristic(
                        name='weightedfreq22-{}8'.format(segment + 1), value=wa3000, recording=rs)
                new_characteristics.extend([c1, c2])
            print('.', end='')
            sys.stdout.flush()

        Characteristic.objects.bulk_create(new_characteristics)
        print('done')

class WeightedFreq28Change(CharacteristicGenerator):

    @classmethod
    def calculate(cls, wave_data, sample_rate):
        freqchanges = {}
        freqchanges = WeightedFreq28.calculate(wave_data, sample_rate)
        for freq_band in range(1, 3):
            for segment in range(1, 8):
                first_value = freqchanges.get('weightedfreq{}2-{}8'.format(freq_band, segment))
                second_value = freqchanges.get('weightedfreq{}2-{}8'.format(freq_band, segment + 1))

                if first_value is None or second_value is None:
                    msg = "Missing weightedfreq value, can't calculate {}-{} change for band {}"\
                            .format(segment, segment + 1, freq_band)
                    logger.warn(msg)
                    continue

                delta = second_value - first_value

                freqchanges['wfreqchange{}2-{}{}8'.format(freq_band, segment, segment + 1)] = delta

        return freqchanges

    @classmethod
    def calculate_bulk(cls, rss):
        print('Calculating 2-bucket, 8-segment weighted frequency change for {} syllables'.format(rss.count()))
        characteristic_names = [
            'wfreqchange{}2-{}{}8'.format(a, b, b + 1) for a in [1, 2] for b in range(1, 8)
        ]
        print(characteristic_names)
        Characteristic.objects.filter(name__in=characteristic_names).delete()
        new_characteristics = []
        for rs in rss:
            for i in range(1, 8):
                for j in range(1, 3):
                    c1 = rs.characteristics.get(name='weightedfreq{}2-{}8'.format(j, i))
                    c2 = rs.characteristics.get(name='weightedfreq{}2-{}8'.format(j, i + 1))
                    delta = c2.value - c1.value
                    c = Characteristic(
                            recording=rs, name='wfreqchange{}2-{}{}8'.format(j, i, i + 1), value=delta)
                    new_characteristics.append(c)
            print('.', end='')
            sys.stdout.flush()
        Characteristic.objects.bulk_create(new_characteristics)
        print()
