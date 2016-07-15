'''
Created on Jun 30, 2016

@author: jivan
'''
from ttlib.characteristics.registry import CharacteristicGeneratorRegistry

class CharacteristicGenerator(object):
    @classmethod
    def calculate_bulk(cls, rss):
        msg = 'Not implemented.  This method is deprecated, please implement and use calculate().'
        raise Exception(msg)

    @classmethod
    def calculate(cls, audio_sample):
        ''' *brief*: Calculates the characteristic(s) encapsulated by the inheriting class.
            *return*: Dictionary of the form {<characteristic_name>: <characteristic_value>, ...}
        '''
        msg = 'Not implemented.  This is a base class, you must inherit & implement calculate()'
        raise Exception(msg)

    @classmethod
    def register(cls):
        CharacteristicGeneratorRegistry.register(cls)
