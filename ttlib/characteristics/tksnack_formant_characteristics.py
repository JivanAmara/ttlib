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

class AverageFormant12(CharacteristicGenerator):
    version = '0.0.0'
    name = 'averageformant12'
    dependencies = []

    @classmethod
    def calculate(cls, wave_data, sample_rate):
        average_formants = {}
        with NamedTemporaryFile(suffix='.wav') as ntf:
            scipy.io.wavfile.write(ntf, sample_rate, wave_data)
            ntf.seek(0)
            s = Sound()
            s.load(ntf.name)
            try:
                all_formants = s.formant()
            except:
                logger.error('Unable to calculate formats')
                return average_formants

        if all_formants is None or len(all_formants) < 8:
            logger.warn('Less than 8 formants')
            return average_formants

        segment_ends = [ int((len(all_formants) / 8.0) * i) for i in range(1, 9)]
        formants = [ [ f[i] for f in all_formants ] for i in range(2) ]
        for i in range(8):
            segment_start = 0 if i == 0 else segment_ends[i - 1]
            segment_end = segment_ends[i]
            avgs = [ average(formants[j][segment_start:segment_end]) for j in range(2) ]

            for formant_index in range(2):
                charname = 'tksnack-formant{}-{}8'.format(formant_index + 1, i + 1)
                average_formants[charname] = avgs[formant_index]

        return average_formants

    @classmethod
    def calculate_bulk(cls, rss):
        print('Generating tksnack-formant1-n8 characteristics for {} syllables.'.format(rss.count()))
        print('Generating tksnack-formant2-n8 characteristics for {} syllables.'.format(rss.count()))

        characteristic_names = [ 'tksnack-formant1-{}8'.format(i) for i in range(1, 9) ]
        characteristic_names.extend([ 'tksnack-formant2-{}8'.format(i) for i in range(1, 9) ])

        Characteristic.objects.filter(name__in=characteristic_names).delete()
        new_characteristics = []
        for count, rs in enumerate(rss, 1):
            with NamedTemporaryFile(suffix='.{}'.format(rs.file_extension)) as ntf:
                ntf.write(rs.content_as_silence_stripped_wav)
                ntf.seek(0)
                s = Sound()
                s.load(ntf.name)
                try:
                    all_formants = s.formant()
                except:
                    continue
            if all_formants is None or len(all_formants) < 8: continue

            segment_ends = [ int((len(all_formants) / 8.0) * i) for i in range(1, 9)]
            formants = [ [ f[i] for f in all_formants ] for i in range(2) ]
            for i in range(8):
                segment_start = 0 if i == 0 else segment_ends[i - 1]
                segment_end = segment_ends[i]
                avgs = [ average(formants[j][segment_start:segment_end]) for j in range(2) ]

                for formant_index in range(2):
                    charname = 'tksnack-formant{}-{}8'.format(formant_index + 1, i + 1)
                    c = Characteristic(
                        recording=rs, name=charname, value=avgs[formant_index]
                    )
                    new_characteristics.append(c)

            if count % 100 == 0:
                print('.', end='')
                sys.stdout.flush()

        Characteristic.objects.bulk_create(new_characteristics)
        print('done')
        sys.stdout.flush()

class AverageFormant1Change(CharacteristicGenerator):
    version = '0.0.0'
    name = 'averageformant1change'
    dependencies = ['averageformant12', ]

    @classmethod
    def calculate(cls, wave_data, sample_rate):
        formant1changes = {}
        avgformants = AverageFormant12.calculate(wave_data, sample_rate)
        for i in range(1, 8):
            first_value = avgformants.get('tksnack-formant1-{}8'.format(i))
            second_value = avgformants.get('tksnack-formant1-{}8'.format(i + 1))

            if first_value is None or second_value is None:
                msg = "Missing formant1 value, can't calculate {}-{} change".format(i, i + 1)
                logger.warn(msg)
                continue

            delta = second_value - first_value

            formant1changes['tksnack-formant1-change-{}{}8'.format(i, i + 1)] = delta

        return formant1changes

    @classmethod
    def calculate_bulk(cls, rss):
        print('Generating tksnack-formant1-change-nm8 characteristics for {} syllables.'\
                .format(rss.count())
        )
        characteristic_names = [ 'tksnack-formant1-change-{}{}8'.format(i, i + 1) for i in range(1, 8) ]
        Characteristic.objects.filter(name__in=characteristic_names).delete()
        new_characteristics = []
        failed = 0
        ok = 0
        for count, rs in enumerate(rss):
            for i in range(1, 8):
                first_value = [ c.value for c in rs.characteristics.all()
                                    if c.name == 'tksnack-formant1-{}8'.format(i) ]
                second_value = [ c.value for c in rs.characteristics.all()
                                    if c.name == 'tksnack-formant1-{}8'.format(i + 1) ]
                if len(first_value) != 1 or len(second_value) != 1:
                    failed += 1
                    continue

                delta = second_value[0] - first_value[0]
                c = Characteristic(
                    recording=rs, name='tksnack-formant1-change-{}{}8'.format(i, i + 1), value=delta
                )

                new_characteristics.append(c)
                ok += 1

            if count % 100 == 0:
                print('.', end='')
                sys.stdout.flush()

        Characteristic.objects.bulk_create(new_characteristics)
        print('done')
        print('Ok: {}, Failed: {}'.format(ok, failed))
        sys.stdout.flush()

class AverageFormant2Change(CharacteristicGenerator):
    name = 'averageformant2change'
    dependencies = ['averageformant12', ]

    @classmethod
    def calculate(cls, wave_data, sample_rate):
        formant2changes = {}
        avgformants = AverageFormant12.calculate(wave_data, sample_rate)
        for i in range(1, 8):
            first_value = avgformants.get('tksnack-formant2-{}8'.format(i))
            second_value = avgformants.get('tksnack-formant2-{}8'.format(i + 1))

            if first_value is None or second_value is None:
                msg = "Missing formant1 value, can't calculate {}-{} change".format(i, i + 1)
                logger.warn(msg)
                continue

            delta = second_value - first_value

            formant2changes['tksnack-formant2-change-{}{}8'.format(i, i + 1)] = delta

        return formant2changes

    @classmethod
    def calculate_bulk(cls, rss):
        print('Generating tksnack-formant2-change-nm8 characteristics for {} syllables.'\
                .format(rss.count())
        )
        characteristic_names = [ 'tksnack-formant2-change-{}{}8'.format(i, i + 1) for i in range(1, 8) ]
        Characteristic.objects.filter(name__in=characteristic_names).delete()
        new_characteristics = []
        failed = 0
        ok = 0
        for count, rs in enumerate(rss):
            for i in range(1, 8):
                first_value = [ c.value for c in rs.characteristics.all()
                                    if c.name == 'tksnack-formant2-{}8'.format(i) ]
                second_value = [ c.value for c in rs.characteristics.all()
                                    if c.name == 'tksnack-formant2-{}8'.format(i + 1) ]
                if len(first_value) != 1 or len(second_value) != 1:
                    failed += 1
                    continue

                delta = second_value[0] - first_value[0]
                c = Characteristic(
                    recording=rs, name='tksnack-formant2-change-{}{}8'.format(i, i + 1), value=delta
                )

                new_characteristics.append(c)
                ok += 1

            if count % 100 == 0:
                print('.', end='')
                sys.stdout.flush()

        Characteristic.objects.bulk_create(new_characteristics)
        print('done')
        print('Ok: {}, Failed: {}'.format(ok, failed))
        sys.stdout.flush()
