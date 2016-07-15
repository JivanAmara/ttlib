'''
Created on Jul 14, 2016

@author: jivan
'''
import pytest
from tempfile import NamedTemporaryFile
import hashlib
import os
from ttlib.normalization.interface import normalize_pipeline

# content of test_class.py
class TestNormalization:
    m4a_audio_path = os.path.join(os.path.dirname(__file__), 'audio_sample.m4a')
    m4a_expected_hash = '60889fd8ea7f43f65ee852b5cd650d24'

    mp3_audio_path = os.path.join(os.path.dirname(__file__), 'audio_sample.mp3')
    mp3_expected_hash = 'ab413274e93765de788c42e081083014'

    def test_normalize_pipeline(self):
        outfile_m4a = NamedTemporaryFile(suffix='.wav')
        normalize_pipeline(self.m4a_audio_path, outfile_m4a.name)
        outfile_m4a.seek(0)
        m = hashlib.md5()
        m.update(outfile_m4a.read())
        outfile_m4a.close()
        m4a_hash = m.hexdigest()

        outfile_mp3 = NamedTemporaryFile(suffix='.wav')
        normalize_pipeline(self.mp3_audio_path, outfile_mp3.name)
        m = hashlib.md5()
        m.update(outfile_mp3.read())
        outfile_mp3.close()
        mp3_hash = m.hexdigest()

        assert m4a_hash == self.m4a_expected_hash
        assert mp3_hash == self.mp3_expected_hash
