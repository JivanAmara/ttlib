'''
Created on Jun 30, 2016

@author: jivan
'''

class CharacteristicGeneratorRegistry(object):
    _charclasses = []

    @classmethod
    def register(cls, CharacteristicClass):
        if CharacteristicClass not in cls._charclasses:
            cls._charclasses.append(CharacteristicClass)

    @classmethod
    def generators(cls):
        return list(cls._charclasses)
