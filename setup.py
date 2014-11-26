from setuptools import setup


with open("README.rst") as fd:
    readme_text = fd.read()

setup(
    name='olimex-ekg-emg',
    version='0.1.0',
    description='A package for gathering data from the Olimex EKG/EMG Shield.',
    license='BSD',
    long_description=readme_text,
    author='Paul Logston',
    author_email='code@logston.me',
    url='https://github.com/logston/olimex-ekg-emg',
    test_suite='tests',
    keywords=['Olimex', 'EKG', 'EMG', 'Arduino'],
    install_requires=[
        'pyserial>=2.7',
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
