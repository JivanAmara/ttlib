'''
Created on Jul 5, 2016

@author: jivan
'''
from __future__ import print_function, unicode_literals
import sys
from tkinter import Tk
from tempfile import NamedTemporaryFile
# from analytics.models import Characteristic
from numpy import average
from tkSnack3 import initializeSnack, Sound
from ttlib.characteristics.generator_base import CharacteristicGenerator
from logging import getLogger
import scipy.io.wavfile

logger = getLogger(__name__)

root = Tk()
initializeSnack(root)

class AveragePitch(CharacteristicGenerator):

    @classmethod
    def calculate(cls, wave_data, sample_rate):
        avgpitches = {}
        with NamedTemporaryFile(suffix='.{}'.format('.wav')) as ntf:
            scipy.io.wavfile.write(ntf, sample_rate, wave_data)
            ntf.seek(0)
            s = Sound()
            s.load(ntf.name)
            pitches = s.pitch()
        if pitches is None or len(pitches) < 8:
            logger.warn('Less than 8 pitch values')
            return avgpitches

        segment_ends = [ int((len(pitches) / 8.0) * i) for i in range(1, 9)]
        for i in range(8):
            segment_start = 0 if i == 0 else segment_ends[i - 1]
            segment_end = segment_ends[i]
            avgpitch = average(pitches[segment_start:segment_end])
            avgpitches['tksnack-pitch-{}8'.format(i + 1)] = avgpitch

        return avgpitches

    @classmethod
    def calculate_bulk(cls, rss):
        characteristic_names = [ 'tksnack-pitch-{}8'.format(i) for i in range(1, 9) ]
        Characteristic.objects.filter(name__in=characteristic_names).delete()
        new_characteristics = []
        for count, rs in enumerate(rss, 1):
            with NamedTemporaryFile(suffix='.{}'.format(rs.file_extension)) as ntf:
                ntf.write(rs.content_as_silence_stripped_wav)
                ntf.seek(0)
                s = Sound()
                s.load(ntf.name)
                pitches = s.pitch()
            if pitches is None or len(pitches) < 8: continue

            segment_ends = [ int((len(pitches) / 8.0) * i) for i in range(1, 9)]
            for i in range(8):
                segment_start = 0 if i == 0 else segment_ends[i - 1]
                segment_end = segment_ends[i]
                avgpitch = average(pitches[segment_start:segment_end])
                c = Characteristic(recording=rs, name='tksnack-pitch-{}8'.format(i + 1), value=avgpitch)
                new_characteristics.append(c)

            if count % 100 == 0:
                print('.', end='')
                sys.stdout.flush()

        Characteristic.objects.bulk_create(new_characteristics)
        print('done')
        sys.stdout.flush()

class AveragePitchChange(CharacteristicGenerator):

    @classmethod
    def calculate(cls, wave_data, sample_rate):
        pitchchanges = {}
        pitches = AveragePitch.calculate(wave_data, sample_rate)
        for i in range(1, 8):
            first_value = pitches.get('tksnack-pitch-{}8'.format(i))
            second_value = pitches.get('tksnack-pitch-{}8'.format(i + 1))

            if first_value is None or second_value is None:
                msg = "Missing pitch value, can't calculate {}-{} change".format(i, i + 1)
                logger.warn(msg)
                continue

            delta = second_value - first_value

            pitchchanges['tksnack-pitch-change-{}{}8'.format(i, i + 1)] = delta

        return pitchchanges

    @classmethod
    def calculate_bulk(cls, rss):
        characteristic_names = [ 'tksnack-pitch-change-{}{}8'.format(i, i + 1) for i in range(1, 8) ]
        Characteristic.objects.filter(name__in=characteristic_names).delete()
        new_characteristics = []
        for count, rs in enumerate(rss):
            for i in range(1, 8):
                first_value = [ c.value for c in rs.characteristics.all()
                                    if c.name == 'tksnack-pitch-{}8'.format(i) ]
                second_value = [ c.value for c in rs.characteristics.all()
                                    if c.name == 'tksnack-pitch-{}8'.format(i + 1) ]
                if len(first_value) != 1 or len(second_value) != 1:
                    continue

                delta = second_value[0] - first_value[0]
                c = Characteristic(
                    recording=rs, name='tksnack-pitch-change-{}{}8'.format(i, i + 1), value=delta
                )

                new_characteristics.append(c)
#                 print('.', end='')
#                 sys.stdout.flush()
                if count % 100 == 0:
                    print('.', end='')
                    sys.stdout.flush()

        Characteristic.objects.bulk_create(new_characteristics)
        print('done')
        sys.stdout.flush()
