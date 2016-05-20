from setuptools import setup
import os

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# README file
with open('README.rst', 'r') as rmf:
    README = rmf.read()

setup(
    name="analytics",
    version="0.1.0",
    author="Jivan Amara",
    author_email="Development@JivanAmara.net",
    packages=['analytics', 'analytics.migrations'],
    package_data={
        'analytics': [
            'requirements.txt',
        ],
    },
    description='Django app for analyzing recorded Pinyin syllables',
    long_description=README,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
    ],
)
