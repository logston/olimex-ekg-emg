"""
This module defines logic for plotting, in real-time, exg data.

update_generator: A generator function that will update the exg figure.

show_exg: A function that will create a new matplotlib figure and make
          a call to animation.FuncAnimation to begin plotting the exg.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from olimex.exg import PacketStreamReader
from olimex.utils import calculate_heart_rate


def update_generator(ax, port):
    """
    Update exg figure.
    :param ax:
    :param port:
    """
    samples_per_graph = 2560
    period_multiplier = 2

    ax.set_ylim(0, 1024)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    # initialize plot with zeros
    data = np.zeros(samples_per_graph)
    line, = ax.plot(data)

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
        ax.set_ylim(amin - margin, amax + margin)
        yield


def show_exg(port):
    """
    Create and display a real-time exg figure.
    :param port:
    :return:
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