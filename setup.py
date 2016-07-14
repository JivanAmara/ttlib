from setuptools import setup
import os

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# README file
with open('README.rst', 'r') as rmf:
    README = rmf.read()

setup(
    name="ttlib",
    version="0.0.0",
    author="Jivan Amara",
    author_email="Development@JivanAmara.net",
    packages=['ttlib'],
    package_data={
        'ttlib': [
            'requirements.txt',
        ],
    },
    description='Python library for recognizing the tone of a mandarin syllable',
    long_description=README,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
    ],
)
