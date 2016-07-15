'''
Created on Jul 15, 2016

@author: jivan
'''
import pytest
import os

if __name__ == '__main__':
    test_path = os.path.join(os.path.dirname(__file__), 'tests')
    pytest.main(os.path.join(test_path, 'test_recognizer.py'))
