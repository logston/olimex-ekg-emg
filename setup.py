import os
from setuptools import setup

import olimex

with open("README.rst") as fd:
    README = fd.read()

with open("LICENSE") as fd:
    LICENSE = fd.read()

MOCK_DATA_FILES = os.listdir('mock-data')
MOCK_DATA_FILES = map(lambda f: os.path.join('mock-data', f), MOCK_DATA_FILES)

setup(
    name='olimex-ekg-emg',
    version=olimex.__version__,
    description='A package for gathering data from the Olimex EKG/EMG Shield.',
    license=LICENSE,
    long_description=README,
    author=olimex.__author__,
    author_email=olimex.__email__,
    url='https://github.com/logston/olimex-ekg-emg',
    packages=['olimex'],
    data_files=[('olimex/mock-data', MOCK_DATA_FILES)],
    test_suite='tests',
    keywords=['Olimex', 'EKG', 'EMG', 'Arduino'],
    install_requires=[
        'bokeh>=0.12.2',
        'pyserial>=2.7',
        'numpy>=1.9.1',
        'scipy>=0.15.1',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
    ],
)
