'''
Created on Jul 14, 2016

@author: jivan
'''
import pickle
import os
import ttlib as analytics

class ToneRecognizer():
    _consensus_predictor = None
    _consensus_predictor_pickle_path = \
        os.path.join(os.path.dirname(__file__), 'consensus_predictor.p')

    def __init__(self):
        if ToneRecognizer._consensus_predictor is None:
            with open(self._consensus_predictor_pickle_path, 'rb') as pf:
                ToneRecognizer._consensus_predictor = pickle.load(pf)

    def get_tone(self, sample_characteristics):
        tone, ignored_score = ToneRecognizer._consensus_predictor.predict(sample_characteristics)
        return tone
