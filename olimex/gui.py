import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from olimex.exg import PacketStreamReader
from olimex.utils import calculate_heart_rate


def update_generator(ax, port):
    samples_per_graph = 2560
    samples_per_update = 12

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
        while len(new_samples) < samples_per_update:
            values = next(reader)
            if values:
                lead_value = values[1] * 0.5  # Transform
                new_samples.append(lead_value)
        data = np.concatenate((data[samples_per_update:], np.array(new_samples)))
        # Add new data to plot
        line.set_ydata(data)

        # Calculate heart rate
        heart_rate = calculate_heart_rate(data)
        ax.text(0.98, 0.95, '{} HR'.format(heart_rate),
                fontsize=15, transform=ax.transAxes, horizontalalignment='right')

        # Calibrate y axis limits
        amax = np.amax(data)
        amin = np.amin(data)
        total_amplitude = amax - amin
        margin = total_amplitude * 0.1
        ax.set_ylim(amin - margin, amax + margin)
        yield


def show_exg(port):
    fig, ax = plt.subplots()
    update_gen = update_generator(ax, port)
    animation.FuncAnimation(fig, lambda _: next(update_gen), interval=50)
    plt.show()


if __name__ == '__main__':
    port = '/dev/tty.usbmodem1411'
    show_exg(port)