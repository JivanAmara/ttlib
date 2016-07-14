'''
Created on Jul 14, 2016

@author: jivan
'''
from ttlib.characteristics.frequency_characteristics import MaxFreq8, MaxFreqChange8
from ttlib.characteristics.sigfreq_characteristic import SigFreq8
from ttlib.characteristics.tksnack_formant_characteristics import AverageFormant12, \
    AverageFormant1Change, AverageFormant2Change
from ttlib.characteristics.tksnack_pitch_characteristics import AveragePitch, AveragePitchChange
from ttlib.characteristics.volume_characteristics import MaxVolume8, MaxVolumeChange8
from ttlib.characteristics.weightedfreq28_characteristic import WeightedFreq28, WeightedFreq28Change

def generate_all_characteristics(wave_data, sample_rate):
    ''' | *brief*: Generate all available characteristics for *audio_sample*
        | *return*: A dictionary of the form { <characteristic name>: <characteristic value>, ... }
    '''
    # All characteristic generator classes
    cgs = [MaxFreq8, MaxFreqChange8,
           SigFreq8,
           AverageFormant12, AverageFormant1Change, AverageFormant2Change,
           AveragePitch, AveragePitchChange,
           MaxVolume8, MaxVolumeChange8,
           WeightedFreq28, WeightedFreq28Change,
    ]

    characteristics = {}
    for CharGenerator in cgs:
        characteristics.update(CharGenerator.calculate(wave_data, sample_rate))

    return characteristics

