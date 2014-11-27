

def calculate_values_from_packet_data(data):
    """
    Return a list of the 6 channel values parsed from the packet data.

    Data sent from the Olimex shield is in the following form:
        uint16_t   data[6];

    Each uint16_t holds a 10-bit sample (= 0 - 1023) in big endian
    (Motorola) format.

    :param data:
    :rtype: list
    """
    values = []

    for index in range(0, len(data), 2):
        # byte_a is the most significant byte and byte_b is
        # the least significant byte.
        byte_a, byte_b = data[index], data[index + 1]
        values.append((byte_a << 8) | byte_b)

    return values


def calculate_heart_rate(data):
    return 60