'''
Created on Jul 14, 2016

@author: jivan
'''
import pickle

class ToneRecognizer():
    _consensus_predictor = None

    def __init__(self, pickle_filename='consensus_predictor.p'):
        if ToneRecognizer._consensus_predictor is None:
            ToneRecognizer._consensus_predictor = pickle.load(pickle_filename)

    def get_tone(self, sample_characteristics):
        tone, ignored_score = ToneRecognizer._consensus_predictor.predict(sample_characteristics)
        return tone
