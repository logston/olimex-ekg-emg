from setuptools import setup

import olimex

with open("README.rst") as fd:
    README = fd.read()


setup(
    name='olimex-ekg-emg',
    version=olimex.__version__,
    description='A package for gathering data from the Olimex EKG/EMG Shield.',
    license='BSD',
    long_description=README,
    author='Paul Logston',
    author_email='code@logston.me',
    url='https://github.com/logston/olimex-ekg-emg',
    test_suite='tests',
    keywords=['Olimex', 'EKG', 'EMG', 'Arduino'],
    install_requires=[
        'pyserial>=2.7',
        'numpy>=1.9.1',
        'scipy>=0.14.0',
        'matplotlib>=1.4.2',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Education',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
    ],
)
