'''
Created on Jul 14, 2016

@author: jivan
'''
from ttlib.characteristics.interface import generate_all_characteristics
import os
import scipy.io.wavfile

class TestCharacteristicGeneration:
    normalized_audio_path = os.path.join(
        os.path.dirname(__file__), 'audio_sample.mp3.normalized.wav'
    )
    expected_characteristic_names = set(['freqchange128', 'freqchange238', 'freqchange348', 'freqchange458', 'freqchange568', 'freqchange678', 'freqchange788', 'maxfreq18', 'maxfreq28', 'maxfreq38', 'maxfreq48', 'maxfreq58', 'maxfreq68', 'maxfreq78', 'maxfreq88', 'maxvolume', 'maxvolume18', 'maxvolume28', 'maxvolume38', 'maxvolume48', 'maxvolume58', 'maxvolume68', 'maxvolume78', 'maxvolume88', 'sigfreq12-18', 'sigfreq12-28', 'sigfreq12-38', 'sigfreq12-48', 'sigfreq12-58', 'sigfreq12-68', 'sigfreq12-78', 'sigfreq12-88', 'sigfreq22-18', 'sigfreq22-28', 'sigfreq22-38', 'sigfreq22-48', 'sigfreq22-58', 'sigfreq22-68', 'sigfreq22-78', 'sigfreq22-88', 'tksnack-formant1-18', 'tksnack-formant1-28', 'tksnack-formant1-38', 'tksnack-formant1-48', 'tksnack-formant1-58', 'tksnack-formant1-68', 'tksnack-formant1-78', 'tksnack-formant1-88', 'tksnack-formant1-change-128', 'tksnack-formant1-change-238', 'tksnack-formant1-change-348', 'tksnack-formant1-change-458', 'tksnack-formant1-change-568', 'tksnack-formant1-change-678', 'tksnack-formant1-change-788', 'tksnack-formant2-18', 'tksnack-formant2-28', 'tksnack-formant2-38', 'tksnack-formant2-48', 'tksnack-formant2-58', 'tksnack-formant2-68', 'tksnack-formant2-78', 'tksnack-formant2-88', 'tksnack-formant2-change-128', 'tksnack-formant2-change-238', 'tksnack-formant2-change-348', 'tksnack-formant2-change-458', 'tksnack-formant2-change-568', 'tksnack-formant2-change-678', 'tksnack-formant2-change-788', 'tksnack-pitch-18', 'tksnack-pitch-28', 'tksnack-pitch-38', 'tksnack-pitch-48', 'tksnack-pitch-58', 'tksnack-pitch-68', 'tksnack-pitch-78', 'tksnack-pitch-88', 'tksnack-pitch-change-128', 'tksnack-pitch-change-238', 'tksnack-pitch-change-348', 'tksnack-pitch-change-458', 'tksnack-pitch-change-568', 'tksnack-pitch-change-678', 'tksnack-pitch-change-788', 'volumechange128', 'volumechange238', 'volumechange348', 'volumechange458', 'volumechange568', 'volumechange678', 'volumechange788', 'weightedfreq12-18', 'weightedfreq12-28', 'weightedfreq12-38', 'weightedfreq12-48', 'weightedfreq12-58', 'weightedfreq12-68', 'weightedfreq12-78', 'weightedfreq12-88', 'weightedfreq22-18', 'weightedfreq22-28', 'weightedfreq22-38', 'weightedfreq22-48', 'weightedfreq22-58', 'weightedfreq22-68', 'weightedfreq22-78', 'weightedfreq22-88', 'wfreqchange12-128', 'wfreqchange12-238', 'wfreqchange12-348', 'wfreqchange12-458', 'wfreqchange12-568', 'wfreqchange12-678', 'wfreqchange12-788', 'wfreqchange22-128', 'wfreqchange22-238', 'wfreqchange22-348', 'wfreqchange22-458', 'wfreqchange22-568', 'wfreqchange22-678', 'wfreqchange22-788'])

    def test_generate_all_characteristics(self):
        sample_rate, wave_data = scipy.io.wavfile.read(self.normalized_audio_path)
        cs = generate_all_characteristics(wave_data, sample_rate)
        print(sorted(cs.keys()))
        assert set(cs.keys()) == self.expected_characteristic_names
