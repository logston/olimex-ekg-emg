olimex-ekg-emg
==============

|docs| |downloads| |latest| |versions| |implementations| |dev_status| |license|

A Python package for gathering and viewing data from the `Olimex EKG/EMG Shield`_.


NOTICE
------

THIS SOFTWARE DOES NOT PROVIDE MEDICAL ADVICE

The information provided by this software is not medical advice. By using this software,
You acknowledge that this software does not and should not be construed to provide
health-related or medical advice, or clinical decision support, or to provide,
support or replace any diagnosis, recommendation, advice, treatment or decision by an
appropriately trained and licensed physician, or to create a patient-physician relationship.
You hereby agree that this software will not be relied on or used, in whole or in part,
for any of the preceding purposes by or on Your behalf with respect to any individual(s).
If You believe You suffer from any medical condition, whether or not this software's
results support this belief, You should immediately seek professional medical advice
or consult with a qualified medical professional.


Installation
------------

::

    pip install olimex-ekg-emg


Usage
-----

First run both Jupyter Noteobook and Bokeh's server:

In one terminal window:

::

    $ jupyter notebook

In another terminal window:

::

    $ bokeh serve

Then from within a Jupyter notebook cell:

::

    from olimex.nb import exg; exg(<port or mock data name>)

This will start a new browser tab/window where the EKG will appear. the value
passed to the ``exg`` function can be a port (eg. `/dev/tty.usbmodem1411`, `COM1`)
or the name of a mock data file (`nsr.bin`).

To list all available ports that may be sending EKG data, use:

::

    from olimex.utils import list_serial_ports

    list_serial_ports()

To list all mock data:

::

    from olimex.utils import get_mock_data_list

    _, mock_data = get_mock_data_list()
    mock_data

Example Output
--------------

.. image:: https://github.com/logston/olimex-ekg-emg/raw/master/docs/images/nsr.gif


Further Documentation
---------------------

Further documentation can be found on `Read the Docs`_.

.. _Read the Docs: http://olimex-ekg-emg.readthedocs.org/en/latest/

.. |docs| image:: https://readthedocs.org/projects/olimex-ekg-emg/badge/
    :alt: Documentation Status
    :scale: 100%
    :target: http://olimex-ekg-emg.readthedocs.org/en/latest/

.. |downloads| image:: https://pypip.in/download/olimex-ekg-emg/badge.svg?period=month
    :target: https://pypi.python.org/pypi/olimex-ekg-emg
    :alt: Downloads

.. |latest| image:: https://pypip.in/version/olimex-ekg-emg/badge.svg?text=version
    :target: https://pypi.python.org/pypi/olimex-ekg-emg/
    :alt: Latest Version

.. |versions| image:: https://pypip.in/py_versions/olimex-ekg-emg/badge.svg
    :target: https://pypi.python.org/pypi/olimex-ekg-emg/
    :alt: Supported Python versions

.. |implementations| image:: https://pypip.in/implementation/olimex-ekg-emg/badge.svg
    :target: https://pypi.python.org/pypi/olimex-ekg-emg/
    :alt: Supported Python implementations

.. |dev_status| image:: https://pypip.in/status/olimex-ekg-emg/badge.svg
    :target: https://pypi.python.org/pypi/olimex-ekg-emg/
    :alt: Development Status

.. |license| image:: https://pypip.in/license/olimex-ekg-emg/badge.svg
    :target: https://pypi.python.org/pypi/olimex-ekg-emg/
    :alt: License

.. _matplotlib figure: http://matplotlib.org/api/figure_api.html#figure

.. _Olimex EKG/EMG Shield: https://www.olimex.com/Products/Duino/Shields/SHIELD-EKG-EMG/
