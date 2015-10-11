import os
import pip
import sys

import numpy as np


def calculate_values_from_packet_data(data):
    """
    Return a list of the 6 channel values parsed from the packet data.

    :param data:
    :rtype: list

    Data sent from the Olimex shield is in the following form:
        ``uint16_t   data[6];``

    Each ``uint16_t`` holds a 10-bit sample (= 0 - 1023) in big endian
    (Motorola) format.

    However the data argument, passed in a call to this function,
    contains a list of length 12; each item in the list is
    a :py:func:`bytes` of length 1.
    """
    values = []

    for index in range(0, len(data), 2):
        # byte_a is the most significant byte and byte_b is
        # the least significant byte.
        byte_a, byte_b = data[index], data[index + 1]
        val = (byte_a << 8) | byte_b
        # For some reason the data comes in upside down.
        # Flip data around a horizontal axis.
        val = (val - 1024) * -1
        values.append(val)

    return values


def calculate_heart_rate(data):
    return np.fft.rfft(data)


def get_mock_data_list():
    pkgs = pip.get_installed_distributions()
    pkgs = [pkg for pkg in pkgs if pkg.project_name == 'olimex-ekg-emg']
    if not pkgs:
        return '', []

    mock_data_dir = os.path.join(pkgs[0].location, 'olimex', 'mock-data')
    if not os.path.exists(mock_data_dir):
        # possibly installed with `pip install -e .`
        mock_data_dir = os.path.join(pkgs[0].location, 'mock-data')

    if not os.path.exists(mock_data_dir):
        return '', []

    return mock_data_dir, os.listdir(mock_data_dir)

