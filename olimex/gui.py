"""
This module defines logic for plotting exg data in real-time.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from olimex.exg import PacketStreamReader
from olimex.utils import calculate_heart_rate


def update_generator(axes, port):
    """
    Update exg figure.

    This function will update the exg figure.

    :param axes:
    :param port:
    """
    samples_per_graph = 2560
    period_multiplier = 2

    axes.set_ylim(0, 1024)
    axes.xaxis.set_visible(False)
    axes.yaxis.set_visible(False)

    # initialize plot with zeros
    data = np.zeros(samples_per_graph)
    line, = axes.plot(data)

    # instantiate a packet reader
    reader = PacketStreamReader(port)

    while True:
        new_samples = []
        packets_in_waiting = reader.packets_in_waiting
        while len(new_samples) / period_multiplier < packets_in_waiting:
            values = next(reader)
            if values:
                lead_value = values[1]
                # Transform graph, stretch the x axis
                for _ in range(period_multiplier):
                    new_samples.append(lead_value)

        data = np.concatenate((data[packets_in_waiting * period_multiplier:],
                               np.array(new_samples)))
        # Add new data to plot
        line.set_ydata(data)

        # TODO
        # Calculate heart rate
        # heart_rate = calculate_heart_rate(data)
        # ax.text(0.98, 0.95, '{} HR'.format(heart_rate),
        #         fontsize=15, transform=ax.transAxes, horizontalalignment='right')

        # Calibrate y axis limits
        amax = np.amax(data)
        amin = np.amin(data)
        total_amplitude = amax - amin
        margin = total_amplitude * 0.1
        axes.set_ylim(amin - margin, amax + margin)
        yield


def show_exg(port):
    """
    Create and display a real-time :ref:`exg <exg>` figure.

    This function will create a new matplotlib figure and make
    a call to :py:class:`~matplotlib.animation.FuncAnimation` to
    begin plotting the :ref:`exg <exg>`.

    :param port: Serial port being sent exg packets.
    :type port: str
    """
    fig, ax = plt.subplots()
    update_gen = update_generator(ax, port)
    animation.FuncAnimation(fig, lambda _: next(update_gen), interval=50)
    plt.show()


if __name__ == '__main__':
    default_port = '/dev/tty.usbmodem1411'
    port = input('Path of com port (default: {}): '.format(default_port))
    if not port:
        port = default_port
    show_exg(port)