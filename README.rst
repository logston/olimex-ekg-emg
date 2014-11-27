olimex-ekg-emg
==============

|docs|

A Python package for gathering and viewing data from the `Olimex EKG/EMG Shield`_.

Installation
------------

::

    pip install olimex-ekg-emg


Usage
-----

::

    >>> from olimex.gui import show_exg
    >>> show_exg('/path/to/port')

Replace ``'/path/to/port'`` with the path to the port to which your Arduino is connected.

A `matplotlib figure`_ should appear and a real-time wave form should begin go to be drawn.
Calibration of the waveform within the figure make take up to 10 seconds.


Further Documentation
---------------------

Further documentation can be found on `Read the Docs`_.

.. _Read the Docs: http://olimex-ekg-emg.readthedocs.org/en/latest/

.. |docs| image:: https://readthedocs.org/projects/olimex-ekg-emg/badge/
    :alt: Documentation Status
    :scale: 100%
    :target: http://olimex-ekg-emg.readthedocs.org/en/latest/

.. _matplotlib figure: http://matplotlib.org/api/figure_api.html#figure

.. _Olimex EKG/EMG Shield: https://www.olimex.com/Products/Duino/Shields/SHIELD-EKG-EMG/