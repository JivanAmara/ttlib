'''
Created on Jun 30, 2016

@author: jivan
'''
from __future__ import print_function
# from analytics.models import Characteristic
import sys
from io import StringIO
import scipy.io.wavfile
from ttlib.characteristics.generator_base import CharacteristicGenerator
from logging import getLogger

logger = getLogger(__name__)

class MaxVolume8(CharacteristicGenerator):

    @classmethod
    def calculate(cls, wave_data, sample_rate):
        maxvolumes = {}
        m = max(wave_data)
        maxvolumes['maxvolume'] = m

        segment_ends = [ (len(wave_data) * i / 8) for i in range(0, 9) ]
        for i in range(8):
            m = max(wave_data[segment_ends[i]:segment_ends[i + 1]])
            maxvolumes['maxvolume{}8'.format(i + 1)] = m

        return maxvolumes

    @classmethod
    def calculate_bulk(cls, rss):
        """ Calculate the max volume for each of 8 segments for each RecordedSyllable in rss.
        """
        print('Calculating 8-segment max volume for {} syllables'.format(rss.count()))
        characteristic_names = [ 'maxvolume{}8'.format(i) for i in range(1, 9) ]
        characteristic_names.append('maxvolume')
        print(characteristic_names)
        Characteristic.objects.filter(name__in=characteristic_names).delete()
        new_characteristics = []
        for rs in rss:
            sio = StringIO(rs.content_as_silence_stripped_wav)
            sample_rate, wave_data = scipy.io.wavfile.read(sio)
            sio.close()
            m = max(wave_data)
            c = Characteristic(recording=rs, name='maxvolume', value=m)
            new_characteristics.append(c)

            segment_ends = [ (len(wave_data) * i / 8) for i in range(0, 9) ]
            for i in range(8):
                m = max(wave_data[segment_ends[i]:segment_ends[i + 1]])
                c = Characteristic(recording=rs, name='maxvolume{}8'.format(i + 1), value=m)
                new_characteristics.append(c)
            print('.', end='')
            sys.stdout.flush()
        Characteristic.objects.bulk_create(new_characteristics)
        print()

class MaxVolumeChange8(CharacteristicGenerator):

    @classmethod
    def calculate(cls, wave_data, sample_rate):
        volumechanges = {}
        volumes = MaxVolume8.calculate(wave_data, sample_rate)
        for i in range(1, 8):
            first_value = volumes.get('maxvolume{}8'.format(i))
            second_value = volumes.get('maxvolume{}8'.format(i + 1))

            if first_value is None or second_value is None:
                msg = "Missing volume value, can't calculate {}-{} change".format(i, i + 1)
                logger.warn(msg)
                continue

            delta = second_value - first_value

            volumechanges['volumechange{}{}8'.format(i, i + 1)] = delta

        return volumechanges

    @classmethod
    def calculate_bulk(cls, rss):
        """ Calculate the change in max volume between each of 8 segments
                for each RecordedSyllable in rss.
        """
        print('Calculating 8-segment volume change for {} syllables'.format(rss.count()))
        characteristic_names = [ 'volumechange{}{}8'.format(i, i + 1) for i in range(1, 8) ]
        print(characteristic_names)
        Characteristic.objects.filter(name__in=characteristic_names).delete()
        new_characteristics = []
        for rs in rss:
            for i in range(1, 8):
                try:
                    c1 = rs.characteristics.get(name='maxvolume{}8'.format(i))
                    c2 = rs.characteristics.get(name='maxvolume{}8'.format(i + 1))
                except Characteristic.DoesNotExist:
                    continue

                delta = c2.value - c1.value
                c = Characteristic(recording=rs, name='volumechange{}{}8'.format(i, i + 1), value=delta)
                new_characteristics.append(c)
            print('.', end='')
            sys.stdout.flush()
        Characteristic.objects.bulk_create(new_characteristics)
        print()
