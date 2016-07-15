'''
Created on Jul 14, 2016

@author: jivan
'''
import pytest
from ttlib.recognizer import ToneRecognizer

class TestToneRecognizer:
    sample_characteristics = {
        'charname': 'charvalue',
        'notreally': 8,
    }
    expected_tone = 8

    def test_get_tone(self):
        tr = ToneRecognizer()
        tone = tr.get_tone(self.sample_characteristics)

        assert tone == self.expected_tone
